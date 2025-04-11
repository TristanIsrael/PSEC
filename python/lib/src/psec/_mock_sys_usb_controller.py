import os, shutil
from psec import MqttClient, ConnectionType, Topics, ResponseFactory, FichierHelper, MqttHelper, NotificationFactory, Constantes
from concurrent.futures import ThreadPoolExecutor

class MockSysUsbController():

    def __init__(self):
        self.__thread_pool = ThreadPoolExecutor(max_workers=1)


    def start(self, source_disk_path:str, storage_path:str, destination_disk_path:str):
        self.source_disk_path = source_disk_path
        self.storage_path = storage_path
        self.destination_disk_path = destination_disk_path

        self.mqtt_client = MqttClient("sys-usb", ConnectionType.TCP_DEBUG, "localhost")
        self.mqtt_client.on_connected = self.__on_mqtt_connected
        self.mqtt_client.on_message = self.__on_mqtt_message
        self.mqtt_client.start()


    def __on_mqtt_connected(self):
        self.__debug("MQTT client connected")
        self.mqtt_client.subscribe("{}/+/+/request".format(Topics.SYSTEM))
        self.mqtt_client.subscribe("{}/+/request".format(Topics.DISCOVER))

        # Finally we announce our components
        self.__handle_discover_components()

        #threading.Timer(10.0, self.__connect_destination).start()


    def __on_mqtt_message(self, topic:str, payload:dict):
        #self.__debug("Message received on topic {}".format(topic))

        self.__thread_pool.submit(self.__message_worker, topic, payload)

    def __message_worker(self, topic:str, payload:dict):
        if topic == "{}/request".format(Topics.LIST_DISKS):
            response = ResponseFactory.create_response_disks_list(["SAPHIR"])
            self.mqtt_client.publish("{}/response".format(Topics.LIST_DISKS), response)

        elif topic == "{}/request".format(Topics.LIST_FILES):            
            self.__handle_list_files(payload)

        elif topic == "{}/request".format(Topics.READ_FILE):
            if not MqttHelper.check_payload(payload, ["disk", "filepath"]):
                self.__debug("Missing arguments")
                return

            disk = payload.get("disk", "")
            filepath = payload.get("filepath", "")

            # Verify and create the local storage if needed
            if not os.path.exists(self.storage_path):
                # Créer le dossier
                os.makedirs(self.storage_path)

            root_path = self.source_disk_path
            source_path = "{}/{}".format(root_path, filepath)
            dest_filepath = "{}/{}".format(self.storage_path, filepath)
            dest_path = os.path.dirname(dest_filepath)

            # Verify and create paths if needed
            #paths = os.path.dirname(source_path)
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

            try:
                shutil.copy(source_path, dest_path)

                source_footprint = FichierHelper.calculate_footprint(source_path)
                dest_footprint = FichierHelper.calculate_footprint(dest_filepath)

                notif = NotificationFactory.create_notification_new_file(Constantes.REPOSITORY, filepath, source_footprint, dest_footprint)
                self.mqtt_client.publish(Topics.NEW_FILE, notif)
            except Exception as e:
                self.__debug("Error during copy: {}".format(e))
                notif = NotificationFactory.create_notification_error(disk, filepath, "The file could not be copied")
                self.mqtt_client.publish(Topics.ERROR, notif)
                return
            

        elif topic == "{}/request".format(Topics.DISCOVER_COMPONENTS):
            self.__handle_discover_components()


        elif topic == "{}/request".format(Topics.COPY_FILE):
            if not MqttHelper.check_payload(payload, ["disk", "filepath", "destination"]):
                self.__debug("Missing arguments for topic {}".format(topic))
                return 
            
            disk = payload.get("disk", "")
            filepath = payload.get("filepath", "")

            source_root_path = self.source_disk_path
            source_path = "{}/{}".format(source_root_path, filepath)
            dest_filepath = "{}/{}".format(self.destination_disk_path, filepath)
            dest_path = os.path.dirname(dest_filepath)            


            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

            try:
                shutil.copy(source_path, dest_path)

                source_footprint = FichierHelper.calculate_footprint(source_path)
                dest_footprint = FichierHelper.calculate_footprint(dest_filepath)                

                if source_footprint != dest_footprint:
                    self.__debug("ERROR: Footprints are not equal")

                response = ResponseFactory.create_response_copy_file(filepath, disk, source_footprint == dest_footprint, source_footprint)
                self.mqtt_client.publish("{}/response".format(Topics.COPY_FILE), response)
            except: 
                notif = NotificationFactory.create_notification_error(disk, filepath, "The file could not be copied")
                self.mqtt_client.publish(Topics.ERROR, notif)

            source_footprint = FichierHelper.calculate_footprint(source_path)


    def __handle_discover_components(self):
        response = {
            "components": [
                { "id": Constantes.PSEC_DISK_CONTROLLER, "label": "System disk controller", "type": "core", "state": "ready" },
                { "id": Constantes.PSEC_INPUT_CONTROLLER, "label": "Input controller", "type": "core", "state": "ready" },
                { "id": Constantes.PSEC_IO_BENCHMARK, "label": "System I/O benchmark", "type": "core", "state": "ready" }
            ]
        }

        self.mqtt_client.publish("{}/response".format(Topics.DISCOVER_COMPONENTS), response)

    def __handle_list_files(self, payload:dict):
        if not MqttHelper.check_payload(payload, ["disk", "recursive", "from_dir"]):
            self.__debug("Missing arguments")
            return

        disk = payload.get("disk")
        recursive = payload.get("recursive", False)
        from_dir = payload.get("from_dir", "")

        if disk != "SAPHIR":
            self.__debug("The disk {} does not exist".format(disk))
            return
        
        root_path = self.source_disk_path
        if not os.path.exists(root_path):
            self.__debug("The folder {} does not exist".format(root_path))
            return                

        files = list()
        FichierHelper.get_folder_contents(root_path, files, len(root_path), recursive, from_dir)

        response = ResponseFactory.create_response_list_files("SAPHIR", files)
        self.mqtt_client.publish("{}/response".format(Topics.LIST_FILES), response)


    def __connect_destination(self):        
        notif = NotificationFactory.create_notification_disk_state("TARGET", "connected")
        self.mqtt_client.publish(Topics.DISK_STATE, notif)

    def __debug(self, message:str):
        print("[SYS-USB] {}".format(message))

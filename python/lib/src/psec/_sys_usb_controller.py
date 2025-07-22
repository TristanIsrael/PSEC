import time
import threading
import os
import base64
import zlib
from pathlib import Path
from queue import Queue
from . import Constantes, Parametres, MqttClient, Topics, MqttHelper
from . import FichierHelper, ResponseFactory, EtatComposant
from . import Logger, Cles, DiskMonitor, NotificationFactory
try:
    from . import DemonInputs
    NO_INPUTS_MONITORING = False
except:
    NO_INPUTS_MONITORING = True
    print("Importing ControleurVmSysUsb without inputs monitoring nor benchmarking capacity")

class SysUsbController():
    """ Cette classe traite les messages échangés par la sys-usb avec le Dom0 ou les autres domaines. """

    __nb_mqtt_conn = 0
    __can_run = True
    __messages_queue = Queue()
    __read_files_queue = Queue()
    __copy_files_queue = Queue()
    __high_priority_messages = [ Topics.LIST_DISKS, Topics.LIST_FILES, Topics.DISCOVER_COMPONENTS, Topics.PING, Topics.SYS_USB_CLEAR_QUEUES ]

    def __init__(self, mqtt_client:MqttClient):
        self.mqtt_client = mqtt_client
        self.__disk_monitor = None
        self.__thread_read_files = threading.Thread(target=self.__read_files_worker, name="read_file_worker")
        self.__thread_copy_files = threading.Thread(target=self.__copy_files_worker, name="copy_file_worker")
        self.__thread_messages = threading.Thread(target=self.__message_worker, name="message_worker")        


    def __del__(self):
        self.__can_run = False


    def start(self):
        self.mqtt_client.on_connected = self.__on_mqtt_connected
        self.mqtt_client.on_message = self.__on_mqtt_message

        self.mqtt_client.start()

        self.__can_run = True

        
    def stop(self):
        self.__can_run = False
        DemonInputs().stop()


    def __on_mqtt_connected(self):
        Logger().setup("USB controller", self.mqtt_client)
        Logger().debug("Starting PSEC disk controller")        

        self.mqtt_client.subscribe(f"{Topics.LIST_DISKS}/request")
        self.mqtt_client.subscribe(f"{Topics.LIST_FILES}/request")
        self.mqtt_client.subscribe(f"{Topics.COPY_FILE}/request")
        self.mqtt_client.subscribe(f"{Topics.READ_FILE}/request")
        self.mqtt_client.subscribe(f"{Topics.DELETE_FILE}/request")
        #self.mqtt_client.subscribe(f"{Topics.BENCHMARK}/request")
        self.mqtt_client.subscribe(f"{Topics.FILE_FINGERPRINT}/request")
        self.mqtt_client.subscribe(f"{Topics.CREATE_FILE}/request")
        self.mqtt_client.subscribe(f"{Topics.DISCOVER_COMPONENTS}/request")
        self.mqtt_client.subscribe(f"{Topics.PING}/request")
        self.mqtt_client.subscribe(f"{Topics.SYS_USB_CLEAR_QUEUES}/request")

        # Démarrage de la surveillance des entrées
        if not NO_INPUTS_MONITORING:
            DemonInputs().start(self.mqtt_client)

        #ControleurBenchmark().setup(self.mqtt_client)
        # Start threads
        self.__thread_read_files.start()
        self.__thread_copy_files.start()
        self.__thread_messages.start()

        self.__disk_monitor = DiskMonitor(Constantes().constante(Cles.CHEMIN_MONTAGE_USB), self.mqtt_client)
        threading.Thread(target=self.__disk_monitor.start).start()

        payload = ResponseFactory.create_response_component_state(
            Constantes.PSEC_DISK_CONTROLLER,
            "System Disk controller",
            "sys-usb",
            EtatComposant.READY
        )
        
        self.mqtt_client.publish(f"{Topics.DISCOVER_COMPONENTS}/response", payload)


    def __on_mqtt_message(self, topic:str, payload:dict):
        #Logger().debug("Message received : topic={}, payload={}".format(topic, payload))

        base_topic, _ = topic.rsplit("/", 1)

        # Some messages have a high priority, we don't put them into the queue
        # These tasks should only be small tasks, otherwise they go in the queue
        if base_topic in self.__high_priority_messages:
            threading.Thread(target=self.__handle_message(base_topic, payload)).start()

        self.__messages_queue.put((base_topic, payload))


    def __message_worker(self):
        #Logger().debug("Handle message {}".format(topic))

        while self.__can_run:
            if not self.__messages_queue.empty():
                message = self.__messages_queue.get() # We get a tuple
                topic = message[0]
                payload = message[1]

                self.__handle_message(topic, payload)

            time.sleep(0.1)

    ####
    # Traitement des commandes
    #
    def __handle_message(self, topic:str, payload:dict):
        if topic == Topics.LIST_DISKS:
            self.__handle_list_disks(topic)
        elif topic == Topics.LIST_FILES:
            self.__handle_list_files(topic, payload)
        elif topic == Topics.COPY_FILE:
            self.__handle_copy_file(topic, payload)
        elif topic == Topics.READ_FILE:
            self.__handle_read_file(topic, payload)
        elif topic == Topics.DELETE_FILE:
            self.__handle_remove_file(topic, payload)
        elif topic == Topics.BENCHMARK:
            self.__handle_benchmark(topic, payload)
        elif topic == Topics.FILE_FINGERPRINT:
            self.__handle_file_fingerprint(topic, payload)
        elif topic == Topics.CREATE_FILE:
            self.__handle_create_file(topic, payload)
        elif topic == Topics.DISCOVER_COMPONENTS:
            self.__handle_discover_components(topic, payload)
        elif topic == Topics.DELETE_FILE:
            self.__handle_delete_file(payload)
        elif topic == Topics.PING:
            self.__handle_ping(payload)
        elif topic == Topics.SYS_USB_CLEAR_QUEUES:
            self.__handle_clear_queue()

    def __handle_list_disks(self, topic:str) -> None:
        Logger().debug("Disks list requested")

        # Get list of mount points
        disks = FichierHelper.get_disks_list()
        #print(disks)

        # Génère la réponse
        response = ResponseFactory.create_response_disks_list(disks)
        self.mqtt_client.publish(f"{topic}/response", response)


    def __handle_list_files(self, topic:str, payload: dict) -> None:        
        # Vérifie les arguments de la commande        
        if not MqttHelper.check_payload(payload, ["disk", "recursive", "from_dir"]):
            Logger().error(f"Missing arguments for {topic}")
            return

        disk = payload.get("disk", "")
        recursive = payload.get("recursive", False)
        from_dir = payload.get("from_dir", "")

        if disk == Constantes.REPOSITORY:
            return

        # Récupère la liste des fichiers
        fichiers = FichierHelper.get_files_list(disk, recursive, from_dir)

        # Génère la réponse
        response = ResponseFactory.create_response_list_files(disk, fichiers)
        self.mqtt_client.publish(f"{topic}/response", response)


    def __handle_read_file(self, topic:str, payload: dict):
        # La copie de fichier consiste à lire le fichier depuis le support externe
        # et à le placer dans le dépôt du système.
        # Une empreinte est calculée lors de la copie et transmise dans la réponse
        # Cette fonction est réentrante, le système gère le nombre de copies parallèles
        # en fonction des ressources disponibles.
        # Les arguments de la commande sont :
        # - nom_fichier au format disk:filename
        # - nom_disque_destination
        if not MqttHelper.check_payload(payload, ["disk", "filepath"]):
            Logger().error(f"Missing argument(s) for the command {topic}")
            return
        
        source_disk = payload.get("disk", "")
        filepath = payload.get("filepath", "")
        repository_path:str = Parametres().parametre(Cles.STORAGE_PATH_DOMU)
    
        source_location = f"{Parametres().parametre(Cles.CHEMIN_MONTAGE_USB)}/{source_disk}"
        source_fingerprint = FichierHelper.calculate_fingerprint(f"{source_location}/{filepath}")

        dest_parent_path = Path(f"{repository_path}/{filepath}").parent
        if not dest_parent_path.exists():
            print(f"Création du répertoire {dest_parent_path} dans le dépôt")
            os.makedirs(dest_parent_path.as_posix(), exist_ok= True)

        self.__read_files_queue.put(
            {
                "source_location": source_location, 
                "source_disk": source_disk, 
                "filepath": filepath, 
                "repository_path": repository_path, 
                "source_fingerprint": source_fingerprint
            }
        )
            #self.task_runner.run_task(self.__do_read_file, args=(source_location, source_disk, filepath, repository_path, source_fingerprint,))    

    def __handle_remove_file(self, topic:str, payload: dict):
        #Logger().error("The command remove file is not implemented")
        pass


    def __handle_copy_file(self, topic:str, payload:dict):
        if not MqttHelper.check_payload(payload, ["disk", "filepath", "destination"]):
            Logger().error(f"Missing arguments for the request {topic}")
            return
        
        source_disk = payload.get("disk", "")
        filepath = payload.get("filepath", "")
        target_disk = payload.get("destination", "")
        
        source_location = f"{Parametres().parametre(Cles.CHEMIN_MONTAGE_USB)}/{source_disk}"        
        destination_location = f"{Parametres().parametre(Cles.CHEMIN_MONTAGE_USB)}/{target_disk}"

        try:
            self.__copy_files_queue.put(
                {
                    "source_location": source_location, 
                    "source_disk": source_disk, 
                    "filepath": filepath, 
                    "target_disk": target_disk, 
                    "destination_location": destination_location
                }
            )
            #self.task_runner.run_task(self.__do_copy_file, args=(source_location, filepath, target_disk, destination_location,))
        except Exception:
            Logger().error(f"An error occured while copying the file {filepath} on {target_disk}")
        
        #FichierHelper.copy_file(disk, filepath, destination_folder)


    def __handle_benchmark(self, topic:str, payload:dict):
        module = payload.get("module")

        if module is None:
            Logger().error(f"Argument missing: module. Topic is {topic}")
            return

    def __handle_file_fingerprint(self, topic:str, payload:dict):
        disk = payload.get("disk")
        filepath = payload.get("filepath")
        
        if disk is not None and disk == Constantes.REPOSITORY:
            # Ignored
            return

        if disk is None:
            Logger().error(f"fArgument missing: disk. Topic is {topic}")
            return
        
        if filepath is None:
            Logger().error(f"Argument missing: filepath. Topic is {topic}")
            return
        
        Logger().debug(f"Calculate fingerprint of the file {filepath} on the disk {disk}")

        mount_point = Parametres().parametre(Cles.CHEMIN_MONTAGE_USB)
        fingerprint = FichierHelper.calculate_fingerprint(f"{mount_point}/{disk}/{filepath}")

        Logger().info(f"The fingerprint of the file {disk} on the disk {filepath} is {fingerprint}")

        response = ResponseFactory.create_response_file_fingerprint(filepath, disk, fingerprint)
        self.mqtt_client.publish(f"{topic}/response", response)


    def __handle_create_file(self, topic:str, payload:dict):
        disk = payload.get("disk", "")
        filepath = payload.get("filepath", "")
        base64_data = payload.get("data", "")

        if not MqttHelper.check_payload(payload, ["disk", "filepath", "data"]):
            Logger().error("Missing argument in the create_file command")
            return

        if disk == Constantes.REPOSITORY:
            # Ignored
            return

        decoded = base64.b64decode(base64_data)

        # Check if data were compressed, and uncompress if needed
        compressed = payload.get("compressed", False)
        if compressed:
            data = zlib.decompress(decoded)
        else:
            data = decoded

        mount_point = Parametres().parametre(Cles.CHEMIN_MONTAGE_USB)
        complete_filepath = f"{mount_point}/{disk}/{filepath}"
        
        Logger().debug(f"Create a file {filepath} of size {len(data)} octets on disk {disk}")

        try:
            with open(complete_filepath, 'wb') as f:
                f.write(data)
            f.close()
        except Exception as e:
            Logger().error(f"An error occured while writing to file {complete_filepath}")
            Logger().error(str(e))
            
            response = ResponseFactory.create_response_create_file(filepath, disk, "", False)
            self.mqtt_client.publish(f"{topic}/response", response)
            return

        # On envoie la notification de succès
        fingerprint = FichierHelper.calculate_fingerprint(complete_filepath)
        response = ResponseFactory.create_response_create_file(complete_filepath, disk, fingerprint, True)
        self.mqtt_client.publish(f"{topic}/response", response)

    def __handle_discover_components(self, topic:str, payload:dict) -> None:
        response = {
            "components": [
                { "id": Constantes.PSEC_DISK_CONTROLLER, "domain_name": "sys-usb", "label": "System disk controller", "type": "core", "state": EtatComposant.READY },
                { "id": Constantes.PSEC_INPUT_CONTROLLER, "domain_name": "sys-usb", "label": "Input controller", "type": "core", "state": EtatComposant.READY },
                { "id": Constantes.PSEC_IO_BENCHMARK, "domain_name": "sys-usb", "label": "System I/O benchmark", "type": "core", "state": EtatComposant.READY }
            ]
        }

        self.mqtt_client.publish(f"{topic}/response", response)
    
    def __handle_delete_file(self, payload):
        if not MqttHelper.check_payload(payload, ["disk", "filepath"]):
            Logger().error(f"The command {Topics.DELETE_FILE} misses argument(s)", "Dom0")
            return

        disk = payload["disk"]

        if disk == Constantes.REPOSITORY:
            # This file is the repository so we ignore it
            return

        filepath = payload["filepath"]
        mount_point = Parametres().parametre(Cles.CHEMIN_MONTAGE_USB)
        storage_filepath = f"{mount_point}/{disk}/{filepath}"

        if not FichierHelper().remove_file(storage_filepath):
            Logger().error(f"Removal of file {filepath} from the disk {disk} failed")
        else:
            Logger().info(f"Removed file {filepath} from the disk {disk}")
            
    def __handle_ping(self, payload):
        ping_id = payload.get("id", "")
        data = payload.get("data", "")
        sent_at = payload.get("sent_at", "")
        payload = ResponseFactory.create_response_ping(ping_id, "sys-usb", data, sent_at)

        self.mqtt_client.publish(f"{Topics.PING}/response", payload)


    def __read_files_worker(self):
        while self.__can_run:
            if not self.__read_files_queue.empty():
                next_file = self.__read_files_queue.get()
                source_location = next_file.get("source_location", "")
                source_disk = next_file.get("source_disk", "")
                filepath = next_file.get("filepath", "")
                repository_path = next_file.get("repository_path", "")
                source_fingerprint = next_file.get("source_fingerprint", "")
                self.__do_read_file(source_location, source_disk, filepath, repository_path, source_fingerprint)
            
            time.sleep(0.1)

    def __copy_files_worker(self):
        while self.__can_run:
            if not self.__copy_files_queue.empty():
                next_file = self.__copy_files_queue.get()
                source_location = next_file.get("source_location", "") 
                filepath = next_file.get("filepath", "")
                target_disk = next_file.get("target_disk", "")
                destination_location = next_file.get("destination_location", "")
                self.__do_copy_file(source_location, filepath, target_disk, destination_location)
            
            time.sleep(0.1)

    def __do_read_file(self, source_location:str, source_disk:str, filepath:str, repository_path:str, source_fingerprint:str):
        #self.__debug_threads()

        dest_fingerprint = FichierHelper.copy_file(source_location, filepath, repository_path, source_fingerprint)
        if dest_fingerprint != "":
            notif = NotificationFactory.create_notification_new_file(Constantes.REPOSITORY, filepath, source_fingerprint, dest_fingerprint)
            self.mqtt_client.publish(Topics.NEW_FILE, notif)
        else:
            notif = NotificationFactory.create_notification_error(source_disk, filepath, "The file could not be copied")
            self.mqtt_client.publish(Topics.ERROR, notif)

    def __do_copy_file(self, source_location:str, filepath:str, target_disk: str, target_location:str):        
        #source_filepath = "{}/{}/{}".format(Parametres().parametre(Cles.CHEMIN_MONTAGE_USB), source_disk, filepath)        
        source_fingerprint = FichierHelper.calculate_fingerprint("{}/{}".format(source_location, filepath))
        
        # Création du répertoire de destination si nécessaire
        parent_path = Path(filepath).parent
        if not parent_path.exists():
            print(f"Création du répertoire {parent_path} dans le dépôt")
            os.makedirs(f"{target_location}/{parent_path}", exist_ok= True)

        dest_fingerprint = FichierHelper.copy_file(source_location, filepath, target_location, source_fingerprint)
        if dest_fingerprint != "":
            Logger().debug(f"The file {filepath} has been copied to {target_location}. The fingerprint is {source_fingerprint}")

            # Envoi d'une notification pour informer de la présence d'un nouveau fichier
            notif = NotificationFactory.create_notification_new_file(disk= target_disk, filepath= filepath, source_fingerprint= source_fingerprint, dest_fingerprint= dest_fingerprint)
            self.mqtt_client.publish(f"{Topics.NEW_FILE}/notification", notif)

            response = ResponseFactory.create_response_copy_file(filepath, target_disk, True, dest_fingerprint)            
        else:
            response = ResponseFactory.create_response_copy_file(filepath, target_disk, False, dest_fingerprint)
            Logger().error(f"La copie du fichier {filepath} dans le dépôt a échoué.")

        self.mqtt_client.publish(f"{Topics.COPY_FILE}/response", response)

    def __handle_clear_queue(self):
        while not self.__copy_files_queue.empty():
            self.__copy_files_queue.get()

        while not self.__read_files_queue.empty():
            self.__read_files_queue.get()

    ######## 
    ## Special functions
    ##
    def __debug_threads(self):
        print(f"Active threads: {threading.active_count()}")
        for thread in threading.enumerate():
            print(f"   -> {thread.name}")

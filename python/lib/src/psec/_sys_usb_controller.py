from . import Constantes, Parametres, MqttClient, Topics
from . import FichierHelper, ResponseFactory, EtatComposant
from . import Logger, Cles, BenchmarkId, MqttClient, DiskMonitor, MqttHelper
from . import TaskRunner
try:
    from . import DemonInputs
    #from . import ControleurBenchmark
    NO_INPUTS_MONITORING = False
except:
    NO_INPUTS_MONITORING = True
    print("Importing ControleurVmSysUsb without inputs monitoring nor benchmarking capacity")
from . import NotificationFactory, FichierHelper
import threading, os, base64, zlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

class SysUsbController():
    """ Cette classe traite les messages échangés par la sys-usb avec le Dom0 ou les autres domaines. """

    task_runner = TaskRunner()
    nb_mqtt_conn = 0

    def __init__(self, mqtt_client:MqttClient):
        self.mqtt_client = mqtt_client
        self.__disk_monitor = None
        #self.__thread_pool = ThreadPoolExecutor(max_workers=1)


    def __del__(self):
        self.task_runner.stop()


    def start(self):
        self.mqtt_client.on_connected = self.__on_mqtt_connected
        self.mqtt_client.on_message = self.__on_mqtt_message

        self.mqtt_client.start()

        # Start the worker
        self.task_runner.start()

        
    def stop(self):
        self.task_runner.stop()
        DemonInputs().stop()


    def __on_mqtt_connected(self):
        Logger().setup("USB controller", self.mqtt_client)
        Logger().debug("Starting PSEC disk controller")

        self.mqtt_client.subscribe(f"{Topics.LIST_DISKS}/request")
        self.mqtt_client.subscribe(f"{Topics.LIST_FILES}/request")
        self.mqtt_client.subscribe(f"{Topics.COPY_FILE}/request")
        self.mqtt_client.subscribe(f"{Topics.READ_FILE}/request")
        self.mqtt_client.subscribe(f"{Topics.DELETE_FILE}/request")
        self.mqtt_client.subscribe(f"{Topics.BENCHMARK}/request")
        self.mqtt_client.subscribe(f"{Topics.FILE_FOOTPRINT}/request")
        self.mqtt_client.subscribe(f"{Topics.CREATE_FILE}/request")
        self.mqtt_client.subscribe(f"{Topics.DISCOVER_COMPONENTS}/request")
        self.mqtt_client.subscribe(f"{Topics.DELETE_FILE}/request")
        self.mqtt_client.subscribe(f"{Topics.PING}/request")

        # Démarrage de la surveillance des entrées
        if not NO_INPUTS_MONITORING:
            DemonInputs().start(self.mqtt_client)
            #threading.Thread(target= DemonInputs().demarre()).start()        

        #ControleurBenchmark().setup(self.mqtt_client)

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

        threading.Thread(target=self.__message_worker, args=(topic, payload,)).start()
        #self.__thread_pool.submit(self.__message_worker, topic, payload)


    def __message_worker(self, topic:str, payload:dict):
        #Logger().debug("Handle message {}".format(topic))

        base_topic, _ = topic.rsplit("/", 1)

        if base_topic == Topics.LIST_DISKS:
            self.__handle_list_disks(base_topic)
        elif base_topic == Topics.LIST_FILES:
            self.__handle_list_files(base_topic, payload)
        elif base_topic == Topics.COPY_FILE:
            self.__handle_copy_file(base_topic, payload)
        elif base_topic == Topics.READ_FILE:
            self.__handle_read_file(base_topic, payload)
        elif base_topic == Topics.DELETE_FILE:
            self.__handle_remove_file(base_topic, payload)
        elif base_topic == Topics.BENCHMARK:
            self.__handle_benchmark(base_topic, payload)
        elif base_topic == Topics.FILE_FOOTPRINT:
            self.__handle_file_footprint(base_topic, payload)
        elif base_topic == Topics.CREATE_FILE:
            self.__handle_create_file(base_topic, payload)
        elif base_topic == Topics.DISCOVER_COMPONENTS:
            self.__handle_discover_components(base_topic, payload)
        elif base_topic == Topics.DELETE_FILE:
            self.__handle_delete_file(payload)
        elif base_topic == Topics.PING:
            self.__handle_ping(payload)

    ####
    # Traitement des commandes
    #
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
    
        source_location = "{}/{}".format(Parametres().parametre(Cles.CHEMIN_MONTAGE_USB), source_disk) 
        source_footprint = FichierHelper.calculate_footprint("{}/{}".format(source_location, filepath))     

        dest_parent_path = Path("{}/{}".format(repository_path, filepath)).parent
        if not dest_parent_path.exists():
            print("Création du répertoire {} dans le dépôt".format(dest_parent_path))
            os.makedirs(dest_parent_path.as_posix(), exist_ok= True)

        dest_footprint = FichierHelper.copy_file(source_location, filepath, repository_path, source_footprint)
        if dest_footprint != "":            
            notif = NotificationFactory.create_notification_new_file(Constantes.REPOSITORY, filepath, source_footprint, dest_footprint)
            self.mqtt_client.publish(Topics.NEW_FILE, notif)
        else:
            notif = NotificationFactory.create_notification_error(source_disk, filepath, "The file could not be copied")
            self.mqtt_client.publish(Topics.ERROR, notif)


    def __handle_remove_file(self, topic:str, payload: dict):
        Logger().error("The command remove file is not implemented")
        pass


    def __handle_copy_file(self, topic:str, payload:dict):
        if not MqttHelper.check_payload(payload, ["disk", "filepath", "destination"]):
            Logger().error("Mising arguments for the request {}".format(topic))
            return
        
        source_disk = payload.get("disk", "")
        filepath = payload.get("filepath", "")
        target_disk = payload.get("destination", "")
        
        source_location = "{}/{}".format(Parametres().parametre(Cles.CHEMIN_MONTAGE_USB), source_disk)        
        destination_location = "{}/{}".format(Parametres().parametre(Cles.CHEMIN_MONTAGE_USB), target_disk)

        try:                   
            self.task_runner.run_task(self.__do_copy_file, args=(source_location, filepath, target_disk, destination_location,))
        except Exception:
            Logger().error(f"An error occured while copying the file {filepath} on {target_disk}")
        
        #FichierHelper.copy_file(disk, filepath, destination_folder)


    def __do_copy_file(self, source_location:str, filepath:str, target_disk: str, target_location:str):        
        #source_filepath = "{}/{}/{}".format(Parametres().parametre(Cles.CHEMIN_MONTAGE_USB), source_disk, filepath)        
        source_footprint = FichierHelper.calculate_footprint("{}/{}".format(source_location, filepath))
        
        # Création du répertoire de destination si nécessaire
        parent_path = Path(filepath).parent
        if not parent_path.exists():
            print(f"Création du répertoire {parent_path} dans le dépôt")
            os.makedirs(f"{target_location}/{parent_path}", exist_ok= True)

        dest_footprint = FichierHelper.copy_file(source_location, filepath, target_location, source_footprint)
        if dest_footprint != "":
            Logger().debug(f"The file {filepath} has been copied to {target_location}. The footprint is {source_footprint}")

            # Envoi d'une notification pour informer de la présence d'un nouveau fichier
            notif = NotificationFactory.create_notification_new_file(disk= target_disk, filepath= filepath, source_footprint= source_footprint, dest_footprint= dest_footprint)
            self.mqtt_client.publish(f"{Topics.NEW_FILE}/notification", notif)

            response = ResponseFactory.create_response_copy_file(filepath, target_disk, True, dest_footprint)            
        else:
            response = ResponseFactory.create_response_copy_file(filepath, target_disk, False, dest_footprint)
            Logger().error(f"La copie du fichier {filepath} dans le dépôt a échoué.")

        self.mqtt_client.publish(f"{Topics.COPY_FILE}/response", response)


    def __handle_benchmark(self, topic:str, payload:dict):
        module = payload.get("module")

        if module is None:
            Logger().error(f"Argument missing: module. Topic is {topic}")
            return

    def __handle_file_footprint(self, topic:str, payload:dict):
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
        
        Logger().debug(f"Calculate footprint of the file {filepath} on the disk {disk}")

        mount_point = Parametres().parametre(Cles.CHEMIN_MONTAGE_USB)
        footprint = FichierHelper.calculate_footprint(f"{mount_point}/{disk}/{filepath}")

        Logger().info(f"The footprint of the file {disk} on the disk {filepath} is {footprint}")

        response = ResponseFactory.create_response_file_footprint(filepath, disk, footprint)
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
        footprint = FichierHelper.calculate_footprint(complete_filepath)
        response = ResponseFactory.create_response_create_file(complete_filepath, disk, footprint, True)
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

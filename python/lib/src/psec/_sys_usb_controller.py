from . import Constantes, Parametres, MqttClient, Topics
from . import FichierHelper, ResponseFactory
from . import Logger, Cles, BenchmarkId, MqttClient, DiskMonitor, MqttHelper
from . import TaskRunner
try:
    from . import DemonInputs
    from . import ControleurBenchmark
    NO_INPUTS_MONITORING = False
except:
    NO_INPUTS_MONITORING = True
    print("Importing ControleurVmSysUsb without inputs monitoring nor benchmarking capacity")
from . import NotificationFactory, FichierHelper
import threading, os, base64, zlib
from pathlib import Path

class SysUsbController():
    """ Cette classe traite les messages échangés par la sys-usb avec le Dom0 ou les autres domaines. """

    task_runner = TaskRunner()
    nb_mqtt_conn = 0

    def __init__(self, mqtt_client:MqttClient):
        self.mqtt_client = mqtt_client

    def __del__(self):
        self.task_runner.stop()        

    def start(self):
        self.mqtt_client.on_connected = self.__on_mqtt_connected
        self.mqtt_client.on_message = self.__on_mqtt_message

        self.mqtt_client.start()

        # Démarre du worker 
        self.task_runner.start()

        # Démarrage de la surveillance des entrées
        if NO_INPUTS_MONITORING != True:
            DemonInputs(self.mqtt_client).start()
            #threading.Thread(target= DemonInputs().demarre()).start()        

    def stop(self):
        self.task_runner.stop()
        DemonInputs(self.mqtt_client).stop()

    def __on_mqtt_connected(self):       
        Logger().setup("USB controller", self.mqtt_client)
        Logger().debug("Starting sys-usb controller")
        self.mqtt_client.subscribe("system/+/+/request") # All the system requests

        ControleurBenchmark().setup(self.mqtt_client)

        self.disk_monitor = DiskMonitor(Constantes().constante(Cles.CHEMIN_MONTAGE_USB), self.mqtt_client)
        threading.Thread(target=self.disk_monitor.start).start()        

    def __on_mqtt_message(self, topic:str, payload:dict):
        #Logger().debug("Message received : topic={}, payload={}".format(topic, payload))

        threading.Thread(target=self.__message_worker, args=(topic, payload,)).start()

    def __message_worker(self, topic:str, payload:dict):
        Logger().debug("Handle message {}".format(topic))

        base_topic, _ = topic.rsplit("/", 1)
        print(base_topic)

        if base_topic == Topics.LIST_DISKS:
            self.__handle_list_disks(base_topic)
        elif base_topic == Topics.LIST_FILES:
            self.__handle_list_files(base_topic, payload)
        elif base_topic == Topics.COPY_FILE:
            Logger().error("File copy is not implemented")
            #self.__lit_fichier(commande)
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
        self.mqtt_client.publish("{}/response".format(topic), response)


    def __handle_list_files(self, topic:str, payload: dict) -> None:
        # Vérifie les arguments de la commande        
        disk = payload.get("disk")
        if disk is None:
            # S'il manque un argument on envoie une erreur
            Logger().error("Argument missing: disk. Topic is {}".format(topic))
            return

        if disk == Constantes.REPOSITORY:
            return

        # Récupère la liste des fichiers        
        fichiers = FichierHelper.get_files_list(disk)

        # Génère la réponse
        response = ResponseFactory.create_response_list_files(disk, fichiers)
        self.mqtt_client.publish("{}/response".format(topic), response)


    def __handle_read_file(self, topic:str, payload: dict):
        # La copie de fichier consiste à lire le fichier depuis le support externe
        # et à le placer dans le dépôt du système.
        # Une empreinte est calculée lors de la copie et transmise dans la réponse
        # Cette fonction est réentrante, le système gère le nombre de copies parallèles
        # en fonction des ressources disponibles.
        # Les arguments de la commande sont :
        # - nom_fichier au format disk:filename
        # - nom_disque_destination
        source_disk = payload.get("source_disk")        
        filepath = payload.get("filepath")        

        if source_disk is None:
            Logger().error("Argument missing: source_disk. Topic is {}".format(topic))
            return
        
        if filepath is None:
            Logger().error("Argument missing: filepath. Topic is {}".format(topic))
            return

        try:                   
            self.task_runner.run_task(self.__do_copy_file, args=(topic, payload,))
        except Exception as e:
            Logger().error("An error occured while reading the file {} on {}".format(filepath, source_disk))


    def __handle_remove_file(self, topic:str, payload: dict):
        Logger().debug("Remove file not implemented")
        Logger().error("The command remove file is not implemented")
        pass


    def __do_copy_file(self, topic:str, payload:dict):
        source_disk = payload.get("source_disk")
        filepath = payload.get("filepath")
        target_disk = payload.get("target_disk")

        if source_disk is None:
            Logger().error("Argument missing: source_disk. Topic is {}".format(topic))
            return
        
        if filepath is None:
            Logger().error("Argument missing: filepath. Topic is {}".format(topic))
            return
        
        if target_disk is None:
            Logger().error("Argument missing: filepath. Topic is {}".format(topic))
            return

        source_filepath = "{}/{}/{}".format(Parametres().parametre(Cles.CHEMIN_MONTAGE_USB), source_disk, filepath)
        source_footprint = FichierHelper.calculate_footprint(source_filepath)

        repository_path = Parametres().parametre(Cles.CHEMIN_DEPOT_DOM0)
        # Création du répertoire de destination si nécessaire
        parent_path = Path(filepath).parent
        if not parent_path.exists():
            print("Création du répertoire {} dans le dépôt".format(parent_path))
            os.makedirs("{}/{}".format(repository_path, parent_path), exist_ok= True)

        destination = "{}/{}".format(repository_path, parent_path)

        if FichierHelper.copy_file(source_filepath, destination, source_footprint) == True:
            Logger().debug("The file {} has been copied into the storage. The footprint is {}".format(source_filepath, source_footprint))            

            # Envoi d'une notification pour informer de la présence d'un nouveau fichier
            notif = NotificationFactory.create_notification_new_file(disk= target_disk, filepath= filepath)
            self.mqtt_client.publish("{}/notification".format(Topics.NEW_FILE), notif)

            response = ResponseFactory.create_response_copy_file(True)            
        else:
            response = ResponseFactory.create_response_copy_file(False)
            Logger().error("La copie du fichier {} dans le dépôt a échoué.".format(filepath))

        self.mqtt_client.publish("{}/response".format(topic), response)


    def __handle_benchmark(self, topic:str, payload:dict):
        module = payload.get("module")

        if module is None:
            Logger().error("Argument missing: module. Topic is {}".format(topic))
            return

        if module == BenchmarkId.INPUTS:
            ControleurBenchmark().execute_benchmark_inputs()
        elif module == BenchmarkId.FILES:
            ControleurBenchmark().execute_benchmark_fichiers()
        else:
            Logger().error("The benchmark cannot be started. Unknown module {}.".format(module))


    def __handle_file_footprint(self, topic:str, payload:dict):
        disk = payload.get("disk")
        filepath = payload.get("filepath")
        
        if disk is not None and disk == Constantes.REPOSITORY:
            # Ignored
            return

        if disk is None:
            Logger().error("Argument missing: disk. Topic is {}".format(topic))
            return        
        
        if filepath is None:
            Logger().error("Argument missing: filepath. Topic is {}".format(topic))
            return
        
        Logger().debug("Calculate footprint of the file {} on the disk {}".format(filepath, disk))

        mount_point = Parametres().parametre(Cles.CHEMIN_MONTAGE_USB)
        footprint = FichierHelper.calculate_footprint("{}/{}/{}".format(mount_point, disk, filepath))

        Logger().info("The footprint of the file {} on the disk {} is {}".format(disk, filepath, footprint))

        response = ResponseFactory.create_response_file_footprint(filepath, disk, footprint)
        self.mqtt_client.publish("{}/response".format(topic), response)


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
        complete_filepath = "{}/{}/{}".format(mount_point, disk, filepath)        
        
        Logger().debug("Create a file {} of size {} octets on disk {}".format(filepath, len(data), disk))

        try:
            with open(complete_filepath, 'wb') as f:
                f.write(data)
            f.close()            
        except Exception as e:
            Logger().error("An error occured while writing to file {}".format(complete_filepath))
            Logger().error(str(e))
            
            response = ResponseFactory.create_response_create_file(filepath, disk, "", False)
            self.mqtt_client.publish("{}/response".format(topic), response)
            return

        # On envoie la notification de succès
        footprint = FichierHelper.calculate_footprint(complete_filepath)
        response = ResponseFactory.create_response_create_file(complete_filepath, disk, footprint, True)
        self.mqtt_client.publish("{}/response".format(topic), response)

    def __handle_discover_components(self, topic:str, payload:dict) -> None:
        response = {
            "components": [
                { "id": Constantes.PSEC_DISK_CONTROLLER, "label": "System disk controller", "type": "core" },
                { "id": Constantes.PSEC_INPUT_CONTROLLER, "label": "Input controller", "type": "core" },
                { "id": Constantes.PSEC_IO_BENCHMARK, "label": "System I/O benchmark", "type": "core" }
            ]
        }

        self.mqtt_client.publish("{}/response".format(topic), response)
    
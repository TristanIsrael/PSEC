from . import Constantes
from . import Logger, InputsProxy, FichierHelper, Parametres, Cles
from . import ResponseFactory
from . import MqttClient, Topics
import threading

class Dom0Controller():
    """ Cette classe traite les commandes envoyées par les Domaines et qui concernent le dépôt local et le 
    système en général (supervision, configuration, etc).

    """    

    mqtt_lock = threading.Event()

    def __init__(self, mqtt_client: MqttClient):
        self.mqtt_client = mqtt_client

        # Handle Mqtt messages
        self.mqtt_client.on_connected = self.__on_mqtt_connected
        self.mqtt_client.on_message = self.__on_mqtt_message
        
        Logger().setup("System controller", mqtt_client)

    def start(self):                
        self.mqtt_client.start()
        self.mqtt_lock.wait()
    
    def __on_mqtt_connected(self):
        Logger().debug("Starting Dom0 controller")        
        self.mqtt_client.subscribe("system/+/+/request") # All the system requests
        InputsProxy(self.mqtt_client).demarre()

    def __on_mqtt_message(self, topic:str, payload:dict):
        base_topic, _ = topic.rsplit("/", 1)

        # The message will be handled in a thread        
        threading.Thread(target=self.__message_worker, args=(base_topic,payload,)).start()

    def __message_worker(self, topic:str, payload:dict):
        """ Cette fonction traite uniquement les messages destinés au Dom0 """
        
        Logger().debug("Handle message on Dom0")        

        if topic == Topics.LIST_FILES:
            self.__handle_list_files(topic, payload)
        elif topic == Topics.FILE_FOOTPRINT:
            self.__handle_file_footprint(payload)

    def __handle_list_files(self, topic:str, payload:dict) -> None:
        if not self.__is_storage_request(payload):
                return 

        # Récupère la liste des fichiers                    
        fichiers = FichierHelper.get_files_list(Constantes.REPOSITORY)

        # Génère la réponse
        response = ResponseFactory.create_response_list_files(Constantes.REPOSITORY, fichiers)
        self.mqtt_client.publish("{}/response".format(topic), response)

    def __handle_file_footprint(self, topic:str, payload:dict) -> None:
        if not self.__is_storage_request(payload):
            return 
                    
        filepath = payload.get("filepath")
        disk = payload.get("disk")

        if filepath == None or disk == None:
            # S'il manque un argument on envoie une erreur
            Logger().error("La commande est incomplète : il manque le nom du disque et/ou le chemin du fichier")            
            return
        
        # Calcule l'empreinte
        repository_path = Parametres().parametre(Cles.CHEMIN_DEPOT_DOM0)
        footprint = FichierHelper.calculate_footprint("{}/{}".format(repository_path, filepath))

        Logger().info("Footprint = {}".format(footprint))
        
        # Génère la réponse
        response = ResponseFactory.create_response_file_footprint(filepath, disk, footprint)
        self.mqtt_client.publish("{}/response".format(topic), response)

    def __is_storage_request(self, payload:dict) -> bool:
        if payload.get("disk") is not None:
            return payload.get("disk") == Constantes.REPOSITORY
        else:
            return False
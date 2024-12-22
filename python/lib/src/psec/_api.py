from . import Constantes, RequestFactory, Topics, NotificationFactory
from . import Logger, MqttClient, ConnectionType, Cles, SingletonMeta

class Api(metaclass=SingletonMeta):
    """ Cette classe permet à un programme tiers d'envoyer des commandes ou recevoir des 
    notifications sans avoir à passer par la socket.

    L'API fournit un jeu d'instructions simples permettant d'envoyer les commandes et 
    recevoir les notifications. En revanche elle ne prend pas en charge le formattage des
    commandes, cela étant géré par la classe MessageFactory.

    L'API n'est utilisable que sur un Domaine utilisateur.

    Pour utiliser l'API il suffit d'instancier la classe Api et d'ouvrir la socket en appelant
    la fonction connecte_socket(). Ensuite, les autres fonctions permettent l'envoi et la réception
    de messages et notifications.

    Les commandes ont toutes un fonctionnement asynchrone. Le résultat de l'exécution d'une 
    commande ne sera communiqué qu'au travers d'une notification. Il est donc nécessaire de fournir
    à l'API une fonction de callback permettant de recevoir ces fonctions.

    La fonction de callback est fournie à l'API durant son instanciation. La signature de la fonction de
    callback est la suivante : callback(message : Message) -> None
    """

    __ready_callbacks = list()
    __message_callbacks = list()
    #__sock = None
    __subscriptions = list()
    __shutdown_callbacks = list()


    def start(self, mqtt_client:MqttClient):
        self.mqtt_client = mqtt_client

        self.mqtt_client.on_connected = self.__on_mqtt_connected
        self.mqtt_client.on_message = self.__on_message_received

        self.mqtt_client.start()

    
    def stop(self):
        self.mqtt_client.stop()


    def get_mqtt_client(self):
        return self.mqtt_client


    def add_message_callback(self, callback_fn):
        if callback_fn is not None:
            self.__message_callbacks.append(callback_fn)
        else:
            print("WARNING: message callback function is None")


    def add_ready_callback(self, callback_fn):
        if callback_fn is not None:
            self.__ready_callbacks.append(callback_fn)            
        else:
            print("WARNING: ready callback function is None")


    def add_shutdown_callback(self, callback_fn):
        if callback_fn is not None:
            self.__shutdown_callbacks.append(callback_fn)            
        else:
            print("WARNING: shutdown callback function is None")


    def subscribe(self, topic:str):
        if not topic in self.__subscriptions:
            self.mqtt_client.subscribe(topic)


    ####
    # Fonctions de journalisation
    #
    def debug(self, message : str, module: str = ""):
        Logger().debug(message, module)


    def info(self, message : str, module: str = ""):
        Logger().info(message, module)


    def warn(self, message : str, module: str = ""):
        Logger().warn(message, module)


    def error(self, message : str, module: str = ""):
        Logger().error(message, module)


    def critical(self, message : str, module: str = ""):
        Logger().critical(message, module)


    ####
    # Fonctions de gestion des supports de stockage
    #
    def get_disks_list(self):
        self.mqtt_client.publish("{}/request".format(Topics.LIST_DISKS), {})


    def get_files_list(self, disk: str, recursive:bool = False, from_dir:str = ""):
        payload = RequestFactory.create_request_files_list(disk, recursive, from_dir)
        self.mqtt_client.publish("{}/request".format(Topics.LIST_FILES), payload)


    def read_file(self, disk:str, filepath:str):
        payload = RequestFactory.create_request_read_file(disk, filepath)
        self.mqtt_client.publish("{}/request".format(Topics.READ_FILE), payload)


    def copy_file(self, source_disk:str, filepath:str, destination_disk:str):
        payload = RequestFactory.create_request_copy_file(source_disk, filepath, destination_disk)
        self.mqtt_client.publish("{}/request".format(Topics.COPY_FILE), payload)


    def copy_file_to_storage(self, source_disk:str, filepath:str):        
        self.copy_file(source_disk, filepath, Constantes.REPOSITORY)


    def delete_file(self, filepath:str, disk:str):
        payload = RequestFactory.create_request_delete_file(filepath, disk)
        self.mqtt_client.publish("{}/request".format(Topics.DELETE_FILE), payload)


    def get_file_footprint(self, filepath:str, disk:str):
        payload = RequestFactory.create_request_get_file_footprint(filepath, disk)
        self.mqtt_client.publish("{}/request".format(Topics.FILE_FOOTPRINT), payload)


    def create_file(self, filepath:str, disk:str, contents:bytes):
        payload = RequestFactory.create_request_create_file(filepath, disk, contents)
        self.mqtt_client.publish("{}/request".format(Topics.CREATE_FILE), payload)


    def discover_components(self) -> None:        
        self.mqtt_client.publish("{}/request".format(Topics.DISCOVER_COMPONENTS), {})


    def publish_components(self, components:list) -> None:        
        payload = {
            "components": components
        }
        self.mqtt_client.publish("{}/response".format(Topics.DISCOVER_COMPONENTS), payload)


    ####
    # Fonctions de notification
    #
    def notify_disk_added(self, disk):
        payload = NotificationFactory.create_notification_disk_state(disk, "connected")
        self.mqtt_client.publish("{}".format(Topics.DISK_STATE), payload)
    

    def notify_disk_removed(self, disk):
        payload = NotificationFactory.create_notification_disk_state(disk, "diconnected")
        self.mqtt_client.publish("{}".format(Topics.DISK_STATE), payload)


    def publish(self, topic:str, payload:dict):
        self.mqtt_client.publish(topic, payload)


    def restart_domain(self, domain_name:str):
        payload = RequestFactory.create_request_restart_domain(domain_name)
        self.mqtt_client.publish("{}/request".format(Topics.RESTART_DOMAIN), payload)

    ####
    # Workflow functions
    #
    def shutdown(self):        
        self.mqtt_client.publish("{}/request".format(Topics.SHUTDOWN), {})

    ####
    # Fonctions privées
    #    
    def __on_mqtt_connected(self):
        Logger().setup("Api", self.mqtt_client)
        self.subscribe("{}/+".format(Topics.DISKS))
        self.subscribe("{}/+/response".format(Topics.DISKS))
        self.subscribe("{}/+/response".format(Topics.MISC))
        self.subscribe("{}/+/response".format(Topics.DISCOVER))        
        self.subscribe("{}/response".format(Topics.SHUTDOWN)) 

        for cb in self.__ready_callbacks:
            cb()


    def __on_message_received(self, topic:str, payload:dict):  
        # Intercept shutdown response
        if topic == "{}/response".format(Topics.SHUTDOWN):
            self.__on_shutdown(payload)
            return # Stop here

        for cb in self.__message_callbacks:
            cb(topic, payload)

    def __on_shutdown(self, payload:dict):
        success = payload.get("state", "") == "accepted"   
        reason = payload.get("reason", "")     

        for cb in self.__shutdown_callbacks:
            cb(success, reason)        

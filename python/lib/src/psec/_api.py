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

    ready_callbacks = list()
    message_callbacks = list()
    sock = None

    '''
    def set_mqtt_msg(self, connection_type:ConnectionType = ConnectionType.SERIAL_PORT, connection_string:str = ""):
        self.client_msg = MqttClient(connection_type, connection_string)

    def set_mqtt_log(self, connection_type:ConnectionType = ConnectionType.SERIAL_PORT, connection_string:str = ""):
        self.client_log = MqttClient(connection_type, connection_string)
    '''

    def start(self, identifier:str):
        '''
        if self.client_log is None:
            self.client_log = MqttFactory.create_client_log_domu(self.identifier)

        if self.client_msg is None:
            self.client_msg = MqttFactory.create_client_msg_domu(self.identifier)

        Logger().setup("API", self.client_log)        
        self.client_msg.on_connected = self.__on_messaging_ready        
        '''
        self.identifier = identifier
        self.nb_mqtt = 0   

        self.client_log = MqttClient("Diag logger", ConnectionType.SERIAL_PORT, Constantes().constante(Cles.SERIAL_PORT_LOG))
        self.client_log.on_connected = self.__on_mqtt_connected
        self.client_log.start()

        self.client_msg = MqttClient("Diag messaging", ConnectionType.SERIAL_PORT, Constantes().constante(Cles.SERIAL_PORT_MSG))
        self.client_msg.on_connected = self.__on_mqtt_connected
        self.client_msg.on_message = self.__on_message_received
        self.client_msg.start()        

    def stop(self):
        self.client_msg.stop()
        self.client_log.stop()

    def get_client_msg(self):
        return self.client_msg
    
    def get_client_log(self):
        return self.client_log

    def __on_mqtt_connected(self):
        self.nb_mqtt += 1        
        if self.nb_mqtt == 2:
            Logger().setup(self.identifier, self.client_log)
            self.__on_messaging_ready()

    def add_message_callback(self, callback_fn):
        if callback_fn is not None:
            self.message_callbacks.append(callback_fn)
        else:
            Logger().warn("WARNING: message callback function is None")

    def add_ready_callback(self, callback_fn):
        if callback_fn is not None:
            self.ready_callbacks.append(callback_fn)
        else:
            Logger().warn("WARNING: ready callback function is None")

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
        self.client_msg.publish("{}/request".format(Topics.LIST_DISKS), {})

    def get_files_list(self, disk: str):
        payload = RequestFactory.create_request_files_list(disk)
        self.client_msg.publish("{}/request".format(Topics.LIST_FILES), payload)

    def read_file(self, disk:str, filepath:str):
        payload = RequestFactory.create_request_read_file(disk, filepath)
        self.client_msg.publish("{}/request".format(Topics.READ_FILE), payload)

    def copy_file(self, source_disk:str, filepath:str, destination_disk:str):
        payload = RequestFactory.create_request_copy_file(source_disk, filepath, destination_disk)
        self.client_msg.publish("{}/request".format(Topics.COPY_FILE), payload)

    def copy_file_to_storage(self, source_disk:str, filepath:str):        
        self.copy_file(source_disk, filepath, Constantes.REPOSITORY)

    def delete_file(self, filepath:str, disk:str):
        payload = RequestFactory.create_request_delete_file(filepath, disk)
        self.client_msg.publish("{}/request".format(Topics.DELETE_FILE), payload)

    def get_file_footprint(self, filepath:str, disk:str):
        payload = RequestFactory.create_request_get_file_footprint(filepath, disk)
        self.client_msg.publish("{}/request".format(Topics.FILE_FOOTPRINT), payload)

    def create_file(self, filepath:str, disk:str, contents:bytes):
        payload = RequestFactory.create_request_create_file(filepath, disk, contents)
        self.client_msg.publish("{}/request".format(Topics.CREATE_FILE), payload)

    def discover_modules(self) -> None:        
        self.client_msg.publish("{}/request".format(Topics.DISCOVER_MODULES), {})

    ####
    # Fonctions de notification
    #
    def notify_disk_added(self, disk):
        payload = NotificationFactory.create_notification_disk_state(disk, "connected")
        self.client_msg.publish("{}".format(Topics.DISK_STATE), payload)
    
    def notify_disk_removed(self, disk):
        payload = NotificationFactory.create_notification_disk_state(disk, "diconnected")
        self.client_msg.publish("{}".format(Topics.DISK_STATE), payload)

    ####
    # Fonctions privées
    #    
    def __on_messaging_ready(self):
        for cb in self.ready_callbacks:
            cb()

    def __on_message_received(self, topic:str, payload:dict):        
        for cb in self.message_callbacks:
            cb(topic, payload)
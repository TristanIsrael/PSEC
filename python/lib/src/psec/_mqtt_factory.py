from . import MqttClient, ConnectionType, Constantes, Cles

class MqttFactory():

    @staticmethod
    def create_mqtt_client_domu(identifier:str) -> MqttClient:
        return MqttClient(identifier, ConnectionType.SERIAL_PORT, Constantes().constante(Cles.SERIAL_PORT_MSG))
    
    @staticmethod
    def create_mqtt_client_dom0(identifier:str) -> MqttClient:
        return MqttClient(identifier, ConnectionType.UNIX_SOCKET, Constantes().constante(Cles.MQTT_MSG_BROKER_SOCKET))
    
    @staticmethod
    def create_mqtt_network_dev(identifier:str) -> MqttClient:
        return MqttClient(identifier, ConnectionType.TCP_DEBUG, "localhost")
    
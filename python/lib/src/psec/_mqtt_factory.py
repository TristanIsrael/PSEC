from . import MqttClient, ConnectionType, Constantes, Cles

class MqttFactory():

    @staticmethod
    def create_client_log_domu(identifier:str) -> MqttClient:
        return MqttClient(identifier, ConnectionType.SERIAL_PORT, Constantes.constante(Cles.SERIAL_PORT_LOG))    

    @staticmethod
    def create_client_msg_domu(identifier:str) -> MqttClient:
        return MqttClient(identifier, ConnectionType.SERIAL_PORT, Constantes.constante(Cles.SERIAL_PORT_MSG))
from psec import MqttClient, ConnectionType, Constantes, Cles, Dom0Controller

if __name__ == "__main__":
    client_log = MqttClient("Dom0 logger", ConnectionType.UNIX_SOCKET, Constantes().constante(Cles.MQTT_LOG_BROKER_SOCKET))
    client_log.start()
    
    client_msg = MqttClient("Dom0 messaging", ConnectionType.UNIX_SOCKET, Constantes().constante(Cles.MQTT_MSG_BROKER_SOCKET))
    client_msg.start()

    ctrl = Dom0Controller(client_msg, client_log)
    ctrl.start()
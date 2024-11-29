from psec import MqttClient, ConnectionType, Constantes, Cles, Dom0Controller

nb_conn = 0
def on_connected():
    global nb_conn
    nb_conn += 1
    print(nb_conn)
    if nb_conn == 2:
        ctrl = Dom0Controller(client_msg, client_log)
        ctrl.start()

if __name__ == "__main__":
    client_log = MqttClient("Dom0 logger", ConnectionType.UNIX_SOCKET, Constantes().constante(Cles.MQTT_LOG_BROKER_SOCKET))
    client_log.on_connected = on_connected
    client_log.start()
    
    client_msg = MqttClient("Dom0 messaging", ConnectionType.UNIX_SOCKET, Constantes().constante(Cles.MQTT_MSG_BROKER_SOCKET))
    client_log.on_connected = on_connected
    client_msg.start()
    
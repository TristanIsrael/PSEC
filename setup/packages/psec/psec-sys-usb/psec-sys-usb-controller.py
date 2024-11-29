from psec import SysUsbController, MqttClient, ConnectionType, Constantes, Cles

nb_conn = 0
def on_connected():
    global nb_conn
    nb_conn += 1
    print(nb_conn)
    if nb_conn == 2:
        c=SysUsbController(client_msg, client_log)
        c.start()

client_log = MqttClient("sys-usb logger", ConnectionType.SERIAL_PORT, Constantes().constante(Cles.SERIAL_PORT_LOG))
client_log.on_connected = on_connected
client_log.start()

client_msg = MqttClient("sys-usb messaging", ConnectionType.SERIAL_PORT, Constantes().constante(Cles.SERIAL_PORT_MSG))
client_msg.on_connected = on_connected
client_msg.start()


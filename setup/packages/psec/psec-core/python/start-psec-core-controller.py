from psec import MqttClient, ConnectionType, Constantes, Cles, Dom0Controller, MqttFactory
import time

if __name__ == "__main__":    
    mqtt_client = MqttFactory.create_mqtt_client_dom0("Core controller")

    ctrl = Dom0Controller(mqtt_client)
    ctrl.start()
from psec import SysUsbController, MqttFactory

if __name__ == "__main__":
    mqtt_client = MqttFactory.create_mqtt_client_domu("sys-usb")

    c=SysUsbController(mqtt_client)
    c.start()


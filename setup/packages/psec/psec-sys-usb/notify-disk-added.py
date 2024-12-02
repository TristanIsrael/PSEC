import sys
from psec import Api, MqttFactory

if len(sys.argv) < 2:
    print("Argument missing : {} disk_name".format(sys.argv[0]))
    exit(-1)

name = sys.argv[1]

def on_api_connected():    
    api.info("The disk {} has been connected to the system.".format(name))
    api.notify_disk_added(name)
    api.stop()
    exit(0)

mqtt_client = MqttFactory.create_mqtt_client_domu("sys-usb")

api = Api("notify-disk-added")
api.add_ready_callback(on_api_connected)
api.start(mqtt_client)
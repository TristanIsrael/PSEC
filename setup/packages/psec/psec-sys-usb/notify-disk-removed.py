import sys, threading
from psec import Api, MqttFactory

if len(sys.argv) < 2:
    print("Argument missing : {} disk_name".format(sys.argv[0]))
    exit(-1)

name = sys.argv[1]

api_ready = threading.Event()
def on_api_connected():
    api_ready.set()

mqtt_client = MqttFactory.create_mqtt_client_domu("notify-disk-removed")

api = Api()
api.add_ready_callback(on_api_connected)
api.start(mqtt_client)

api_ready.wait()

api.info("The disk {} has been disconnected from the system.".format(name))
api.notify_disk_removed(name)
api.stop()
exit(0)
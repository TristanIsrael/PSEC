import sys, threading
from psec import Api, MqttFactory

if len(sys.argv) < 2:
    print(f"Argument missing : {sys.argv[0]} disk_name")
    exit(1)

name = sys.argv[1]

api_ready = threading.Event()
def on_api_connected():
    api_ready.set()

mqtt_client = MqttFactory.create_mqtt_client_domu("notify-disk-added")

api = Api()
api.add_ready_callback(on_api_connected)
api.start(mqtt_client)

api_ready.wait()

api.info(f"The disk {name} has been connected to the system.")
api.notify_disk_added(name)
api.stop()
mqtt_client.stop()
exit(0)

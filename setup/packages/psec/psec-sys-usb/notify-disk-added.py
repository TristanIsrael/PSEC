import sys
from psec import Api

if len(sys.argv) < 2:
    print("Argument missing : {} disk_name".format(sys.argv[0]))
    exit(-1)

def on_api_connected():
    nom = sys.argv[1]
    api.notify_disk_added(nom)
    exit(0)

api = Api("notify-disk-added")
api.add_ready_callback(on_api_connected)
api.start()
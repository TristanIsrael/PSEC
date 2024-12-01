import sys
from psec import Api

if len(sys.argv) < 2:
    print("Argument missing : {} disk_name".format(sys.argv[0]))
    exit(-1)

name = sys.argv[1]

def on_api_connected():    
    api.info("The disk {} has been disconnected from the system.".format(name))
    api.notify_disk_removed(name)
    api.stop()
    exit(0)

api = Api("notify-disk-removed")
api.add_ready_callback(on_api_connected)
api.start()
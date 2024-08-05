import sys
from psec import Api

if len(sys.argv) < 2:
    print("Argument missing : {} disk_name".format(sys.argv[0]))
    exit(-1)

def on_api_connected():
    nom = sys.argv[1]
    api.notifie_ajout_disque(nom)
    exit(0)

api = Api()
api.set_ready_callback(on_api_connected)
api.demarre()
import sys
from psec import Api

if len(sys.argv) < 2:
    print("Argument missing : {} disk_name".format(sys.argv[0]))
    exit(-1)

api = Api()
if api.demarre():    
    nom = sys.argv[1]
    api.notifie_retrait_disque(nom)
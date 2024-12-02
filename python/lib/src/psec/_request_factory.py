from . import Constantes, Domaine, Parametres, Cles

class RequestFactory():
    ''' La classe MessageFactory permet de générer les notification, commandes et
    erreurs utilisées dans le cadre des échanges entre domaines.

    L'émetteur de la commande est automatiquement ajouté lors de sa création.

    Pour rappel les domaines impliqués dans le socle sont :
    - sys-usb qui gère les accès aux supports USB

    Les notification sont les suivantes :
    - Le DomU informe le Dom0 qu'il a démarré (DomU -> Dom0)
    - La sys-usb informe le Dom0 qu'un support USB a été connecté (DomU -> Dom0)
    - La sys-usb informe le Dom0 qu'un support USB a été déconnecté (DomU -> Dom0)

    Les commandes sont les suivantes :
    - Journalisation
      - Un domaine ajoute une entrée dans le journal (Dom* -> Dom0)
      - Le Dom0 enregistre le journal sur le support USB de sortie (DomU -> Dom0)
    - Système
      - Le DomU demande l'état d'activation du débogage (DomU -> Dom0)
      - Le DomU demande le redémarrage du système (DomU -> Dom0)
      - Le DomU demande l'arrêt du système (DomU -> Dom0)
      - Le DomU demande la réinitialisation d'un autre DomU (DomU -> Dom0)
      - Le DomU demande le niveau de charge de la batterie (DomU -> Dom0)
      - Le DomU demande l'état de l'alimentation secteur (DomU -> Dom0)
    - Fichiers
      - Le DomU demande la liste des fichiers d'un support USB (DomU -> Dom0 ; Dom0 -> sys-usb)
      - Le DomU demande la création d'une archive sécurisée sur le support USB de sortie (DomU -> Dom0 ; Dom0 -> sys-usb)
      - Le DomU demande l'ajout d'un fichier à l'archive sécurisée sur le support USB de sortie (DomU -> Dom0 ; Dom0 -> sys-usb)
      - Le DomU demande la copie d'un fichier (DomU -> Dom0 ; Dom0 -> sys-usb)      
    - Notifications
      - Le DomU notifie l'appui sur une touche de clavier (DomU -> Dom0 -> *)
      - Le DomU notifie l'appui sur un bouton de souris (DomU -> Dom0 -> *)
      - Le DomU notifie le déplacement de la souris (DomU -> Dom0 -> *)
      - Le DomU informe le toucher de l'écran tactile (DomU -> Dom0 -> *)
    
    '''    

    @staticmethod
    def create_request_files_list(disk : str) -> dict:
        return { 
            "disk": disk 
            }
    
    @staticmethod
    def create_request_read_file(disk : str, filepath : str) -> dict:
        return {
            "disk": disk,
            "filepath": filepath
        }        
    
    @staticmethod
    def create_request_copy_file(source_disk:str, filepath:str, destination_disk:str) -> dict :
        # Exemple :
        # { filepath: "Mon Disque:/répertoire/fichier", disk_destination: "Autre disque" }
        return {
            "disk": source_disk,
            "filepath": filepath,
            "destination": destination_disk
        }        
    
    @staticmethod
    def create_request_delete_file(filepath : str, disk : str = Constantes().constante(Cles.DEPOT_LOCAL)) -> dict:
        return {
            "filepath": filepath,
            "disk": disk
        }
    
    @staticmethod
    def create_request_start_benchmark(id_benchmark: str):
        return {
            "module": id_benchmark
        }        

    @staticmethod 
    def create_request_get_file_footprint(filepath:str, disk:str) -> dict:
        return {
            "filepath": filepath,
            "disk": disk
        }        
    
    @staticmethod
    def create_request_create_file(filepath:str, disk:str, contents:bytes) -> dict:
        return {
            "filepath": filepath,
            "disk": disk,
            "contents": contents
        }    

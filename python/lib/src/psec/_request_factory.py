from . import Constantes, Parametres, Cles

class RequestFactory():
    """ The class MessageFactory generates notifications, commands and errors
    used in the communication between Domains.
    
    The emitter of the command is automatically added during the creation.

    **Reminder** Domains involved in the foundation are:
    - sys-usb which manages USB devices

    Notification are:

    - A DomU notifies Dom0 he has started (DomU to Dom0)
    - sys-usb notifies Dom0 that a USB storage is connected (DomU to Dom0)
    - sys-usb notifies Dom0 that a USB storage is disconnected (DomU to Dom0)

    Commands are:

    - Logging

      - A Domain adds an entry in the log (DomU to Dom0)
      - Dom0 records the log on a USB storage (DomU to Dom0)

    - System

      - A DomU asks for the debug status (DomU to Dom0)
      - A DomU asks for to reboot of the system (DomU to Dom0)
      - A DomU asks for to shut the system down (DomU to Dom0)
      - A DomU asks for the reset of another DomU (DomU to Dom0)
      - A DomU asks for the batery level (DomU to Dom0)
      - A DomU asks for the charging state (DomU to Dom0)

    - Files

      - A DomU asks for the list of storages (DomU to Dom0 to sys-usb)
      - A DomU asks for the creation of a secure archive on a USB storage (DomU to Dom0 to sys-usb)
      - A DomU asks for adding a file to a secure archive (DomU to Dom0 to sys-usb)
      - A DomU asks for the copy of a file (DomU to Dom0 to sys-usb)    
      
    - Notifications
    
      - To do
    
    """   

    @staticmethod
    def create_request_files_list(disk: str, recursive: bool = False, from_dir: str = "") -> dict:
        return { 
            "disk": disk,
            "recursive": recursive,
            "from_dir": from_dir
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
    def create_request_delete_file(filepath: str, disk: str = Constantes().constante(Cles.DEPOT_LOCAL)) -> dict:
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
    def create_request_create_file(filepath:str, disk:str, contents:bytes, compressed:bool=False) -> dict:
        return {
            "filepath": filepath,
            "disk": disk,
            "data": contents.decode("utf-8"),
            "compressed": compressed
        }    

    @staticmethod
    def create_request_restart_domain(domain_name:str):
        return {
            "domain_name": domain_name
        }
    
    @staticmethod
    def create_request_ping(ping_id, source_name, data, datetime):
        return {
            "id": ping_id,
            "source": source_name,
            "data": data,
            "sent_at": datetime
        }
        
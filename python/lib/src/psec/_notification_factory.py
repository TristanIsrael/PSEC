
class NotificationFactory:
    """ Cette classe permet de créer des notifications simmplement.

    Les fonctions de cette classes sont statiques.
    """

    @staticmethod
    def create_notification_disk_state(disk:str, state:str):
        payload = {
            "disk": disk, 
            "state": state
        }

        return payload

    @staticmethod
    def create_notification_new_file(disk:str, filepath:str) -> dict:
        payload = {            
            "disk": disk,
            "filepath": filepath
        }
        
        return payload
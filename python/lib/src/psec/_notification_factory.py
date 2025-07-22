import psutil

class NotificationFactory:
    """ Cette classe permet de créer des notifications simmplement.

    Les fonctions de cette classes sont statiques.
    """

    @staticmethod
    def create_notification_disk_state(disk:str, state:str) -> dict:
        payload = {
            "disk": disk, 
            "state": state
        }

        return payload

    @staticmethod
    def create_notification_new_file(disk:str, filepath:str, source_fingerprint:str, dest_fingerprint:str) -> dict:
        payload = {            
            "disk": disk,
            "filepath": filepath,
            "source_fingerprint": source_fingerprint,
            "dest_fingerprint": dest_fingerprint
        }
        
        return payload
     
    @staticmethod
    def create_notification_error(disk:str, filepath:str, error:str) -> dict:
        payload = {
            "disk": disk,
            "filepath": filepath,
            "error": error
        }

        return payload
    
    @staticmethod
    def create_notification_energy_state(battery:psutil._common.sbattery) -> dict:
        payload = {
            "battery_level": battery.percent,
            "plugged": 1 if battery.power_plugged else 0
        }

        return payload
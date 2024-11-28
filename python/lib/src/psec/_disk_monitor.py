import os
from watchdog.observers.polling import PollingObserver
from watchdog.events import LoggingEventHandler, FileSystemEventHandler, FileSystemEvent
from . import Logger, NotificationFactory, EtatDisque, Parametres, MqttClient, Topics

class DiskEventHandler(FileSystemEventHandler):
    """ Gère les changements sur le point de montage des supports de stockage"""    

    def __init__(self, client_msg:MqttClient) -> None:
        super().__init__()        
        self.client_msg = client_msg

    def on_moved(self, event:FileSystemEvent) -> None:
        super().on_moved(event)
        # Evénement ignoré

    def on_created(self, event:FileSystemEvent) -> None:
        super().on_created(event)        

        Logger().debug("{} has been added".format(event.src_path))
        if event.is_directory:
            nom_dossier = os.path.basename(event.src_path)
            # Envoi de la notification
            notif = NotificationFactory.create_notification_disk_state(nom_dossier, EtatDisque.PRESENT)            
            self.client_msg.publish("{}/notification".format(Topics.DISK_STATE), notif)
        else:
            Logger().debug("{} ignored".format(event.src_path))

    def on_deleted(self, event: FileSystemEvent) -> None:
        super().on_deleted(event)

        # Envoi de la notification
        Logger().debug("{} has been removed".format(event.src_path))
        if event.is_directory:
            nom_dossier = os.path.basename(event.src_path)
            # Envoi de la notification
            notif = NotificationFactory.cree_notification_disque(nom= nom_dossier, etat= EtatDisque.ABSENT)            
            self.client_msg.publish("{}/notification".format(Topics.DISK_STATE), notif)
        else:
            Logger().debug("{} ignored".format(event.src_path))

    def on_modified(self, event: FileSystemEvent) -> None:
        super().on_modified(event)
        # Evénement ignoré

    def on_closed(self, event: FileSystemEvent) -> None:
        super().on_closed(event)
        # Evénement ignoré

    def on_opened(self, event: FileSystemEvent) -> None:
        super().on_opened(event)
        # Evénement ignoré

class DiskMonitor():
    """ Cette classe surveille un répertoire afin de détecter les ajout et suppression de fichiers et dossiers.

    Elle fonctionne en mode *polling* afin d'être compatible avec le protocole 9pfs de XEN qui ne prend pas en 
    charge les notifications de système de fichiers.

    La classe doit être instanciée avec le chemin du point de montage à surveiller (par exemple /mnt). 
    
    Connexion d'un support de stockage :
    Lorsqu'un support de stockage est connecté, un nouveau point de montage est créé par le système (cf udev/mdev) 
    dans le répertoire /mnt (par exemple /mnt/NO NAME). Dans ce cas, la notification SUPPORT_USB 
    sera émise.

    Déconnexion d'un support de stockage :
    Lorsqu'un support de stockage est retiré, le point de montage est effacé par le système (cf udev/mdev) dans 
    le répertoire /mnt. Dans ce cas, la notification SUPPORT_USB sera émise.
    """    

    def __init__(self, folder:str, client_msg:MqttClient, client_log:MqttClient):
        Logger().setup("Disk monitor", client_log)
        self.folder = folder
        self.client_msg = client_msg

    def demarre(self):
        Logger().debug("Starting disks monitoring on mount point {}".format(self.folder))

        event_handler = DiskEventHandler(self.client_msg)
        observer = PollingObserver()
        observer.schedule(event_handler, self.folder, recursive=False)
        observer.start()
        observer.join()
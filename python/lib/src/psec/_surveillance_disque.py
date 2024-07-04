import os
from watchdog.observers.polling import PollingObserver
from watchdog.events import LoggingEventHandler, FileSystemEventHandler, FileSystemEvent
from panoptiscan_lib import Journal, NotificationFactory, EtatDisque, Parametres, MessagerieDomu

class EvenementDisqueHandler(FileSystemEventHandler):
    """ Gère les changements sur le point de montage des supports de stockage"""

    journal = Journal("")

    def __init__(self, journal:Journal) -> None:
        super().__init__()
        self.journal = journal

    def on_moved(self, event:FileSystemEvent) -> None:
        super().on_moved(event)
        # Evénement ignoré

    def on_created(self, event:FileSystemEvent) -> None:
        super().on_created(event)        

        self.__journalise_debug("L'élément {} a été ajouté".format(event.src_path))
        if event.is_directory:
            nom_dossier = os.path.basename(event.src_path)
            # Envoi de la notification
            notif = NotificationFactory.cree_notification_disque(nom= nom_dossier, etat= EtatDisque.PRESENT)
            self.__journalise_debug(notif.to_json())
            MessagerieDomu().envoie_message_xenbus(notif)
        else:
            self.__journalise_debug("Le fichier {} est ignoré".format(event.src_path))

    def on_deleted(self, event: FileSystemEvent) -> None:
        super().on_deleted(event)

        # Envoi de la notification
        self.__journalise_debug("L'élément {} a été supprimé".format(event.src_path))
        if event.is_directory:
            nom_dossier = os.path.basename(event.src_path)
            # Envoi de la notification
            notif = NotificationFactory.cree_notification_disque(nom= nom_dossier, etat= EtatDisque.ABSENT)
            self.__journalise_debug(notif.to_json())
            MessagerieDomu().envoie_message_xenbus(notif)
        else:
            self.__journalise_debug("Le fichier {} est ignoré".format(event.src_path))

    def on_modified(self, event: FileSystemEvent) -> None:
        super().on_modified(event)
        # Evénement ignoré

    def on_closed(self, event: FileSystemEvent) -> None:
        super().on_closed(event)
        # Evénement ignoré

    def on_opened(self, event: FileSystemEvent) -> None:
        super().on_opened(event)
        # Evénement ignoré

    def __journalise_debug(self, message):
        print(message)
        self.journal.debug(message)

class SurveillanceDisque():
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
    journal = None
    repertoire = None

    def __init__(self, repertoire):
        self.journal = Journal("Surveillance disque ({})".format(repertoire))
        self.repertoire = repertoire

    def demarre(self):
        self.journal.info("Démarrage de la surveillance du disque monté au répertoire {}".format(self.repertoire))

        event_handler = EvenementDisqueHandler(self.journal)
        observer = PollingObserver()
        observer.schedule(event_handler, self.repertoire, recursive=False)
        observer.start()
        observer.join()
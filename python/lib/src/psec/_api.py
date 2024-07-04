import logging, json, threading, socket
from . import Parametres, Cles, Constantes, CommandeFactory, Message, NotificationFactory, EtatDisque, Journal, MessageHelper, MessagerieDomu

class Api():
    """ Cette classe permet à un programme tiers d'envoyer des commandes ou recevoir des 
    notifications sans avoir à passer par la socket.

    L'API fournit un jeu d'instructions simples permettant d'envoyer les commandes et 
    recevoir les notifications. En revanche elle ne prend pas en charge le formattage des
    commandes, cela étant géré par la classe MessageFactory.

    L'API n'est utilisable que sur un Domaine utilisateur.

    Pour utiliser l'API il suffit d'instancier la classe Api et d'ouvrir la socket en appelant
    la fonction connecte_socket(). Ensuite, les autres fonctions permettent l'envoi et la réception
    de messages et notifications.

    Les commandes ont toutes un fonctionnement asynchrone. Le résultat de l'exécution d'une 
    commande ne sera communiqué qu'au travers d'une notification. Il est donc nécessaire de fournir
    à l'API une fonction de callback permettant de recevoir ces fonctions.

    La fonction de callback est fournie à l'API durant son instanciation. La signature de la fonction de
    callback est la suivante : callback(message : Message) -> None
    """

    callback_fn = None
    sock = None
    journal = Journal("API")

    def __init__(self, callback_fn = None):
        self.callback_fn = callback_fn                

    def demarre(self):
        self.journal.debug("Démarrage de la messagerie")
        MessagerieDomu().set_message_callback(self.callback_fn)
        threading.Thread(target= MessagerieDomu().demarre, args= (False, )).start()

    def set_callback_function(self, callback_fn):
        self.callback_fn = callback_fn

    ####
    # Fonctions de journalisation
    #
    def debug(self, message : str):
        self.journal.debug(message)

    def info(self, message : str):
        self.journal.info(message)

    def warn(self, message : str):
        self.journal.warn(message)

    def error(self, message : str):
        self.journal.error(message)

    def critical(self, message : str):
        self.journal.critical(message)

    ####
    # Fonctions de gestion des supports de stockage
    #
    def get_liste_disques(self):
        cmd = CommandeFactory.cree_commande_liste_disques()
        self.__envoie_message(cmd)

    def get_liste_fichiers(self, disque : str):
        cmd = CommandeFactory.cree_commande_liste_fichiers(disque)
        self.__envoie_message(cmd)

    def lit_fichier(self, disk:str, filepath:str):
        cmd = CommandeFactory.cree_commande_lit_fichier(disk, filepath)
        self.__envoie_message(cmd)

    def copie_fichier(self, source_disk:str, filepath:str, destination_disk:str):
        cmd = CommandeFactory.cree_commande_copie_fichier(source_disk, filepath, destination_disk)
        self.__envoie_message(cmd)

    def copie_fichier_dans_depot(self, source_disk:str, filepath:str):        
        self.copie_fichier(source_disk, filepath, Constantes.REPOSITORY)

    def supprime_fichier(self, nom_du_fichier:str, nom_du_disque:str):
        cmd = CommandeFactory.cree_commande_supprime_fichier(nom_du_fichier, nom_du_disque)
        self.__envoie_message(cmd)    

    def get_file_footprint(self, filepath:str, disk:str):
        cmd = CommandeFactory.cree_commande_get_file_footprint(filepath, disk)
        self.__envoie_message(cmd)

    def create_file(self, filepath:str, disk:str, contents:bytes):
        cmd = CommandeFactory.cree_commande_create_file(filepath, disk, contents)
        self.__envoie_message(cmd)

    ####
    # Fonctions de notification
    #
    def notifie_ajout_disque(self, nom_disque):
        notif = NotificationFactory.cree_notification_disque(nom_disque, EtatDisque.PRESENT)
        self.__envoie_message(notif)

    def notifie_retrait_disque(self, nom_disque):
        notif = NotificationFactory.cree_notification_disque(nom_disque, EtatDisque.ABSENT)
        self.__envoie_message(notif)

    ####
    # Fonctions privées
    #
    def __envoie_message(self, message : Message):        
        MessagerieDomu().envoie_message_xenbus(message)
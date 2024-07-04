from . import Constantes, MessagerieDom0, EtatDomu, TypeMessage, TypeEvenement, NotificationFactory
from . import Domaine, Message, Journal, InputsProxy, TypeCommande, FichierHelper, Parametres, Cles
from . import ReponseFactory
import logging, threading

class ControleurDom0():
    """ Cette classe traite les messages échangés par le Dom0, soit par l'API, soit par les sockets Xenbus
    qui sont connectées aux DomU.

    Lorsqu'un message arrive :
      - soit on le traite localement,
      - soit on le route vers un DomU
      - soit on l'envoie à la callback de l'API pour un client local     
    """
    journal = Journal("Contrôleur Dom0")

    etat_domus = {}

    def __init__(self):        
        pass

    def demarre(self):
        self.journal.info("Démarrage du Contrôleur Dom0")

        MessagerieDom0().set_message_callback(self.__on_message_recu)
        MessagerieDom0().demarre()

        InputsProxy().demarre()

    def etat_domu(self, domu : Domaine):
        return self.etat_domus.get(domu)

    def __on_message_recu(self, message : Message):        
        """ Cette fonction traite les messages reçus sur une socket Xenbus (en provenance d'un DomU) ou sur
        la socket de l'API (en provenance d'un client local).

        Les messages sont analysés pour déterminer s'il s'agit d'une notification susceptible de déclencher un
        changement d'état interne, ou d'une action à réaliser sur le Dom0, ou encre d'un message à transférer 
        à un DomU.
        """

        # Les notifications peuvent être à destination du Dom0 ou "broadcast"
        # on les traite dans la même fonction __traite_notification
        if message.type == TypeMessage.NOTIFICATION:
            self.__traite_notification(message)
        #elif message.type == TypeMessage.COMMANDE:
        #    self.__traite_commande(message)

        # Si le message est à destination de Dom0 on le traite
        if message.destination == Domaine.DOM0:
            threading.Thread(target=self.__traite_message_dom0, args=(message,)).start()

        # Le cas échéant on le redirige
        if message.destination != Domaine.DOM0:
            self.__redirige_message(message)

    def __traite_message_dom0(self, message):
        """ Cette fonction traite uniquement les messages destinés au Dom0 """
        self.journal.debug("Traite le message à destination du Dom0")

        if message.commande == TypeCommande.LISTE_FICHIERS:
            arguments = message.payload.get("arguments")
            nom_disque = arguments.get("nom_disque")
            if nom_disque == None:
                # S'il manque un argument on envoie une erreur
                self.journal.error("La commande est incomplète : il manque le nom du disque")            
                return

            # Récupère la liste des fichiers                    
            fichiers = FichierHelper.get_liste_fichiers(nom_disque)

            # Génère la réponse
            reponse = ReponseFactory.cree_reponse_liste_fichiers(nom_disque, fichiers, message.source)
            MessagerieDom0().envoie_message_domu(reponse)
        elif message.commande == TypeCommande.GET_FILE_FOOTPRINT:
            arguments = message.payload.get("arguments")
            filepath = arguments.get("filepath")
            disk = arguments.get("disk")
            if filepath == None or disk == None:
                # S'il manque un argument on envoie une erreur
                self.journal.error("La commande est incomplète : il manque le nom du disque et/ou le chemin du fichier")            
                return

            if disk != Constantes.REPOSITORY:
                self.journal.error("Il ne s'agit pas du dépôt (disk={}). La commande est ignorée.".format(disk))
                return

            # Calcule l'empreinte
            repository_path = Parametres().parametre(Cles.CHEMIN_DEPOT_DOM0)
            footprint = FichierHelper.calculate_footprint("{}/{}".format(repository_path, filepath))

            self.journal.info("Footprint = {}".format(footprint))
            
            # Génère la réponse
            reponse = ReponseFactory.cree_reponse_file_footprint(filepath, disk, footprint)
            reponse.destination = message.source
            MessagerieDom0().envoie_message_domu(reponse)

    def __traite_notification(self, notification):
        self.journal.debug("Traite la notification")
        
        if notification.evenement == TypeEvenement.ETAT_DOMU:
            data = notification.data
            pret = data.get("pret")
            
            if pret == 1:                
                etat = EtatDomu.DEMARRE
            else:
                etat = EtatDomu.ARRETE

            etat_precedent = self.etat_domus.get(notification.source)
            self.etat_domus[notification.source] = etat
            if etat_precedent != etat:
                self.__etat_domu_changed(notification.source)

    def __etat_domu_changed(self, domu):
        # On envoie une notification à tous les Domaines sur le changement d'état
        notif = NotificationFactory.cree_notification_domu_pret(destination = Domaine.TOUS)
        # On injecte le nom du DomU dans la payload
        notif.data["domu"] = domu
        MessagerieDom0().diffuse_message(notif)

    def __redirige_message(self, message : Message):
        self.journal.debug("Redirection du message vers la bonne destination")
        
        # Si besoin on met des règles
        MessagerieDom0().envoie_message_domu(message)
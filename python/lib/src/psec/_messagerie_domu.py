import json, time, socket, logging, threading, os, serial
from . import Constantes, Cles, SingletonMeta, Parametres, ErreurFactory, MessageHelper, CommandeFactory, TypeMessage
from . import TypeCommande, Commande, FichierHelper, Journal, Reponse, Message, TypeReponse

class MessagerieDomu(metaclass=SingletonMeta):
    """Classe permettant l'envoi et la réception de messages entre Domaines utilisateurs et Domaine 0
    
    Elle est utilisée exclusivement par les DomU.

    La messagerie possède deux interfaces : 
    - une vers le Dom0 permettant d'échanger des messages avec lui
    - l'autre vers une socket locale permettant aux autres processus d'envoyer et recevoir des messages
    """

    chemin_socket_xenbus = None
    socket_xenbus = None    
    recv_buffer = bytearray() 
    journal = Journal("Messaging")
    message_callbacks = list()
    demarrage_callbacks = list()
    messagerie_demarree = False

    ### 
    # Fonctions publiques
    #

    def __init__(self):
        pass

    def __del__(self):
        if self.socket_xenbus != None:
            self.socket_xenbus.close()

    def set_demarrage_callback(self, demarrage_callback):    
        if demarrage_callback is not None:
            self.demarrage_callbacks.append(demarrage_callback)

    def set_demarrage_callbacks(self, demarrage_callbacks):    
        for cb in demarrage_callbacks:
            if cb is not None:
                self.demarrage_callbacks.append(cb)

    def set_message_callback(self, message_callback):        
        if message_callback is not None:
            self.message_callbacks.append(message_callback)

    def set_message_callbacks(self, message_callback):      
        for cb in message_callback:  
            if cb is not None:
                self.message_callbacks.append(cb)

    def demarre(self, demon = False, force_serial_port = ""):    
        self.journal.debug("Starting DomU messaging")
            
        if self.messagerie_demarree:
            self.journal.warning("Messaging has already been started")
            return 
        
        if force_serial_port == "":
            self.chemin_socket_xenbus = Parametres().parametre(Cles.CHEMIN_SOCKET_MSG)
        else:
            self.chemin_socket_xenbus = force_serial_port

        th = threading.Thread(target=self.__connecte_interface_xenbus)
        th.daemon = demon
        th.start()

    def arrete(self):
        if not self.messagerie_demarree:
            return
        
        self.messagerie_demarree = False

        if self.socket_xenbus != None:
            self.socket_xenbus.close()

    def envoie_message_xenbus(self, message : Message):
        if self.socket_xenbus == None:
            self.journal.error("Xenbus serial port is not connected")
        else:
            #self.journal.debug(message.to_json())
            self.socket_xenbus.write(message.to_json()+b'\n')
        
    def envoie_erreur_xenbus(self, erreur : dict):                
        msg = json.dumps(erreur, ensure_ascii=False, separators=(',', ':'))
        self.journal.error("Error:")
        self.journal.error(msg)
        #self.envoie_message_xenbus(msg)

    ###
    # Fonctions privées
    #
    def __connecte_interface_xenbus(self):
        #Ouvre le flux avec la socket
        self.journal.debug("Opening Xenbus channel %s" % self.chemin_socket_xenbus)

        try:
            self.socket_xenbus = serial.Serial(port= self.chemin_socket_xenbus)
            self.interface_xenbus_prete = True            
            self.journal.info("Messaging for Domain {} is started".format(Parametres().identifiant_domaine()))            
            self.messagerie_demarree = True
            if len(self.demarrage_callbacks) > 0:                
                for cb in self.demarrage_callbacks:
                    cb()

            while(self.messagerie_demarree):
                data = self.socket_xenbus.read_until(b'\n') #Parametres().parametre(Cles.TAILLE_TRAME))

                if data:
                    #self.journal.debug("Data received from Xenbus : {0}".format(data))
                    #self.recv_buffer.extend(data)
                    
                    # Il se peut que le message arrive en plusieurs morceaux,
                    # ou bien que des morceaux de messages soient assemblés dans une même trame.
                    # Il faut donc extraire un message complet et laisser le reste dans le buffer
                    #endl = self.recv_buffer.find(b'\n')
                    #if endl > -1:                    
                    #self.journal.debug("We have a complete message...")
                        # On extrait le message complet, on le met de côté et on remet le reste dans le buffer
                        #extract = self.recv_buffer[:endl]
                        #self.recv_buffer = self.recv_buffer[endl+1:]

                    try:
                        # Ensuite on décode le message et on le traite
                        #j = json.loads(data)
                        self.__traite_donnees_xenbus(data)                            
                    except Exception as e:
                        self.journal.error("Error: The message could not be decoded.")
                        self.journal.error(data.decode())
                        self.journal.error(e)
                        msg = ErreurFactory.genere_erreur(logging.ERROR, "The message could not be decoded")
                        self.envoie_erreur_xenbus(msg)
            
        except socket.error as e:
            self.socket_xenbus = None
            self.journal.error("Impossible to conect to serial port %s" % self.chemin_socket_xenbus)
            self.journal.error(e)                    

    def __traite_donnees_xenbus(self, message : bytes):
        """ Cette fonction traite un message provenant du XenBus
        
        Un message venant du XenBus peut avoir été par le Dom0 ou par un DomU.
        TODO : gérer les capabilities des DomU pour filtrer les message que ce DomU peut gérer.

        Un message peut avoir été généré par le socle ou être un message métier. Dans le premier
        cas il est traité par un contrôleur du socle, dans l'autre il est transféré directement
        à l'API à un contrôleur externe.
        """
        if len(message) == 0:
            return

        msg = MessageHelper.cree_message_from_json(message)
        if msg == None:
            err = ErreurFactory.genere_erreur(logging.ERROR, "The message is not well formed")
            self.envoie_erreur_xenbus(err)
        else:
            self.journal.debug("The message has been decoded")
            #self.journal.debug(msg.to_json())  

            if msg.source == Parametres().parametre(Cles.IDENTIFIANT_DOMAINE):
                self.journal.debug("Message coming from here, we ignore it")
                return

            try:
                if len(self.message_callbacks) > 0:
                    for cb in self.message_callbacks:
                        cb(msg)
            except Exception as e:
                print(e)
                pass # On ne traite pas les erreurs de la callback

            #if msg.type == TypeMessage.COMMANDE:
            #    self.__traite_commande_xenbus(msg)

    #def __traite_commande_xenbus(self, commande):
    #    if commande.commande == TypeCommande.LISTE_FICHIERS:
    #        if commande.arguments == None:
    #            self.journal.error("La commande liste_fichiers ne contient pas d'argument")
    #            return
    #                                
    #        nom_disque = commande.arguments["nom_disque"]
    #        if nom_disque == None or nom_disque == "":
    #            self.journal.error("Le nom du disque est vide")
    #            return
    #        
    #        fichiers = FichierHelper.get_liste_fichiers(nom_disque)
    #        
    #        # Une fois la liste des fichiers obtenue il faut la renvoyer au demandeur
    #        # La liste des fichiers est transmise directement dans la payload
    #        reponse = Reponse(commande.commande, fichiers)
    #        reponse.destination = commande.source
    #        #self.journal.debug(reponse.to_json())
    #        self.envoie_message_xenbus(reponse)
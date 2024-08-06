import json, time, socket, logging, threading, os, glob
from . import Constantes, Cles, SingletonMeta, Parametres, ErreurFactory, TypeEvenement
from . import MessageHelper, CommandeFactory, Journal, Domaine, Message, TypeMessage

class MessagerieDom0(metaclass=SingletonMeta):
    """Classe permettant l'envoi et la réception de messages entre Domaines utilisateurs et Domaine 0
    
    Elle est utilisée exclusivement par le Dom0.

    La messagerie possède plusierus interfaces : 
    - une socket locale permettant aux autres processus d'envoyer et recevoir des messages
    - une socket vers chaque DomU permettant d'échanger des messages avec lui

    La liste des sockets DomU est gérée dans le fichier de configuration du système (paramètre sockets_xenbus_domu).

    La communication inter-DomU passe obligatoirement par la MessagerieDom0 qui route les messages en fonction de
    la source, la destination et le type de message.

    Cette classe ne traite pas les message mais s'occupe uniquement de la sérialisation-désérialisation des messages
    sur les sockets Xenbus et locale. Le traitement des messages est effectué par la classe ControleurDom0.
    """

    #chemin_socket_locale = None
    sockets_xenbus = []
    buffers_xenbus = []
    socket_locale = None   
    recv_buffer = bytearray() 
    journal = Journal("MessagerieDom0")
    message_callback = None
    messages_recus = []

    def __init__(self):        
        pass

    def __del__(self):
        for nom, socket in self.sockets_xenbus:
            self.journal.debug("Fermeture de la socket avec le DomU {}".format(nom))
            socket.close()
        #if self.socket_locale != None:
        #    self.socket_locale.close()

    ####
    # Fonctions publiques
    #
    def set_message_callback(self, fn):
        self.message_callback = fn

    def demarre(self):   
        self.journal.info("Démarrage de la messagerie Dom0")
        #self.chemin_socket_locale = Parametres().parametre(Cles.CHEMIN_SOCKET_API)  
        
        threading.Thread(target= self.__surveille_sockets_messagerie).start()

    def envoie_erreur_domu(self, domu, erreur):                
        msg = json.dumps(erreur, ensure_ascii=False, separators=(',', ':'))
        #self.envoie_message_domu(msg)
        self.__ecrit_message_domu(domu, msg.encode())

    def diffuse_message(self, message : Message):   
        #print(self.sockets_xenbus)
        #for _, socket in self.sockets_xenbus.items():
        #    socket.send(message.to_json().encode("utf-8"))
        for nom, _ in self.sockets_xenbus.items():
            self.__ecrit_message_domu(nom, message.to_json())

    ####
    # Fonctions privées
    #
    def __surveille_sockets_messagerie(self):
        self.journal.info("Démarrage de la surveillance des sockets de messagerie DomU")

        # Nous devons ouvrir chaque socket de messagerie disponible
        chemin_sockets = self.__chemin_sockets()
        self.journal.debug("Recherche des sockets DomU dans {}".format(chemin_sockets))
        while True:            
            fichiers = glob.glob(chemin_sockets)        
            if len(fichiers) == 0:
                self.journal.info("No messaging socket available")
                self.sockets_xenbus.clear()
            for fichier in fichiers:
                if fichier not in self.sockets_xenbus:
                    threading.Thread(target=self.__connecte_interface_xenbus, args=(fichier,)).start()
            # On attend quelques secondes avant de reboucler
            time.sleep(5)

    def __chemin_sockets(self):
        return "{}/*-msg.sock".format(Parametres().parametre(Cles.CHEMIN_SOCKETS_MESSAGERIE))

    def __connecte_interface_xenbus(self, fichier_socket):
        #Ouvre le flux avec la socket
        nom_domaine = fichier_socket
        if fichier_socket.find("-msg") > -1:
            spl = fichier_socket.split("-msg")
            if len(spl) > 1: 
                spl = spl[0].split("/") # Il s'agit d'un chemin et non uniquement d'un nom de fichier                
                nom_domaine = spl[len(spl)-1]

        if self.sockets_xenbus.get(nom_domaine) != None:
            return # Nous avons déjà une socket pour ce domaine

        self.journal.debug("Try to connect to messaging socket {} for domain {}".format(fichier_socket, nom_domaine))

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sockets_xenbus[nom_domaine] = sock
        self.journal.debug("Messaging socket to domain {} is open".format(nom_domaine))
        try:            
            sock.connect(fichier_socket)  
            recv_buffer = bytearray()                      

            while(True):
                taille = Parametres().parametre(Cles.TAILLE_TRAME)
                data = sock.recv(taille)

                if data:
                    self.journal.debug("Données reçues depuis le Xenbus : {0}".format(data))
                    recv_buffer.extend(data)
                    
                    # Algorithme:
                    # On splitte le message avec \n dans spl
                    # Les len(spl)-1 premiers messages sont complets
                    # Le dernier est complet uniquement s'il se termine par "}"
                    # S'il ne se termine pas par "}" on le remet dans le buffer d'entrée
                    if recv_buffer.find(b'\n') > -1:
                        self.journal.debug("Le buffer contient au moins un message")

                        # La trame peut contenir un ou plusieurs messages complets et/ou des morceaux
                        # de messages. Il faut extraire les messages complets et laisser le reste
                        # dans le buffer
                        # Pour le moment on fait tout le traitement en synchrone.
                        msg_recus = recv_buffer.split(b'\n')
                        dernier_complet = recv_buffer.endswith(b'\n')

                        if dernier_complet:
                            # On ajoute tous les messages à la liste des messages à traiter
                            self.messages_recus.extend(msg_recus) 
                            recv_buffer.clear()
                        else:
                            # On ajoute les messages complets (n-1) à la liste des messages à traiter
                            # puis on remet le dernier dans le buffer
                            self.messages_recus.extend(msg_recus[:len(msg_recus)-1])
                            recv_buffer.clear()
                            recv_buffer.extend(msg_recus[len(msg_recus)-1])

                        self.__traite_prochain_message()
        except socket.error:
            self.journal.error("Connection lost to messaging socket {}".format(fichier_socket))
            self.sockets_xenbus.remove(nom_domaine)

    def __traite_prochain_message(self):
        self.journal.debug("Dépile les messages ({} restant)".format(len(self.messages_recus)))
        if len(self.messages_recus) == 0:
            return
        
        msg_data = self.messages_recus.pop(0)
        try:
            # Ensuite on décode chaque message et on le traite                            
            self.__traite_message_xenbus(msg_data)                            
        except Exception as e:
            self.journal.error("Erreur : Le message ne peut pas être décodé.")
            self.journal.error(e)                            
                #msg = ErreurFactory.genere_erreur(logging.ERROR, "Le message ne peut pas être décodé")
                #self.envoie_erreur_domu(fichier_socket, msg)
            #finally:
            #    recv_buffer.clear()

    #def __cree_interface_locale(self):
    #    #Crée une socket Unix locale
    #    self.journal.debug("Crée une socket UNIX locale %s" % self.chemin_socket_locale)
    #
    #    if os.path.exists(self.chemin_socket_locale):
    #        os.unlink(self.chemin_socket_locale)
    #
    #    try:
    #        self.socket_locale = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)   
    #        self.socket_locale.bind(self.chemin_socket_locale)
    #    except socket.error as e:
    #        self.journal.error("La création de la socket a échoué")
    #        self.journal.error(e)
    #    
    #    while True:
    #        self.socket_locale.listen(10)
    #        connexion, _ = self.socket_locale.accept()
    #        self.journal.debug("Connexion reçue sur la socket locale")
    #        threading.Thread(target=self.__lit_socket_locale, args=(connexion,)).start()            
            
    #def __lit_socket_locale(self, connexion):    
    #    while True:
    #        data = connexion.recv(Parametres.parametre(Cles.TAILLE_TRAME))
    #        if data:
    #            self.journal.debug("Données reçues depuis la socket locale : %s" % data)                
    #
    #            try:
    #                # Ensuite on décode le message et on le traite
    #                j = json.loads(data.decode("utf-8"))
    #                self.__traite_message_local(j)
    #            except Exception:
    #                self.journal.error("Erreur : Le message ne peut pas être décodé.")
    #                self.journal.error(data)
    #                msg = json.dumps(ErreurFactory.genere_erreur(logging.ERROR, "Le message ne peut pas être décodé\n"), separators=(',', ':'))
    #                connexion.send(msg.encode())

    def __traite_message_xenbus(self, donnees : bytes):
        if len(donnees) == 0:
            return
        
        self.journal.debug("Traite le message {}".format(donnees))
        msg = MessageHelper.cree_message_from_json(donnees)

        if msg == None:
            self.journal.error("Le message est mal formaté")
            self.journal.error(donnees)
        else:
            self.journal.debug("Le message a bien été décodé.")

            if self.message_callback != None:                                
                self.journal.debug("Envoi à la callback du contrôleur")
                threading.Thread(target=self.message_callback, args=(msg,)).start()
            else:
                self.journal.debug("Pas de callback définie, fin du traitement pour ce message")

        self.__traite_prochain_message()
        
    #def __traite_message_local(self, message):
    #    pass

    def envoie_message_domu(self, message : Message):
        """ Cette fonction envoit un message vers un unique DomU """

        if message.destination == Domaine.TOUS:
            self.diffuse_message(message)
        else:
            self.__ecrit_message_domu(message.destination, message.to_json())

    def __ecrit_message_domu(self, domu, data : bytes):
        # On retrouve la socket du DomU
            socket = self.sockets_xenbus.get(domu)
            if socket == None:
                self.journal.error("Il n'y a pas de socket pour le DomU {}".format(domu))
                return
            
            # On écrit les données sur la socket
            self.journal.debug("Ecriture sur la socket {}: {}".format(domu, data))
            socket.send(data +b'\n')
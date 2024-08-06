import threading, time, glob, socket, os
from . import Journal, Parametres, Cles, Domaine, SingletonMeta

class InputsProxy(metaclass=SingletonMeta):
    """! La classe InputsProxy agit comme un proxy pour les informations sur les périphériques
    d'entrée

    Les périphériques d'entrée sont raccordés à la VM sys-usb, celle-ci surveille les événements
    de la souris, du clavier et de l'interface tactile. Lorsqu'un événement est déclenché par un
    périphérique, les informations sont transmises au Dom0 au travers du canal inputs et traitées
    directement par cette classe.

    Les événements sont directement copiés vers la VM identifiée comme GUI (paramètre nom_domaine_gui).

    Pour plus de détail sur la nature des informations transmises, consulter la documentation de la classe
    DemonInputs.
    """

    journal = Journal("InputsProxy")
    socket_gui = None
    #messages_recus = []
    domaine_gui = Domaine.INDEFINI

    def demarre(self):
        self.journal.info("Démarrage du proxy inputs")

        # On vérifie qu'un domaine GUI a bien été défini
        self.domaine_gui = Parametres().parametre(Cles.NOM_DOMAINE_GUI)
        if self.domaine_gui == None:
            self.journal.warn("Aucun domaine GUI défini. Le proxy ne sera pas démarré")
            return        
        
        chemin_socket = Parametres().parametre(Cles.CHEMIN_SOCKET_INPUT_DOM0)
        if not os.path.exists(chemin_socket):
            self.journal.warn("Le fichier socket {} n'existe pas".format(chemin_socket))
            return

        if not self.__ouvre_socket_gui():
            self.journal.warn("La socket vers la GUI n'a pas pu être ouverte.")
            return

        threading.Thread(target=self.__ecoute_socket_vm_sys_usb, args=(chemin_socket,)).start()   

    ##
    # Fonctions privées
    #
    def __ecoute_socket_vm_sys_usb(self, fichier_socket):
        #Ouvre le flux avec la socket
        self.journal.debug("Ouvre le canal avec la socket Xenbus {} pour le domaine sys-usb".format(fichier_socket))

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:            
            sock.connect(fichier_socket)  
            self.journal.debug("La socket vers le domaine sys-usb est ouverte")
            recv_buffer = bytearray()

            while(True):
                #taille = Parametres().parametre(Cles.TAILLE_TRAME)
                data = sock.recv(128)

                if data:
                    #self.journal.debug("Données reçues depuis le Xenbus : {0}".format(data))                    
                    # On recopie directement sur le port de la GUI
                    self.socket_gui.send(data)
                        
        except socket.error:
            self.journal.error("Impossible d'ouvrir la socket %s" % fichier_socket)

    def __ouvre_socket_gui(self):
        #Ouvre le flux avec la socket
        chemin_fichier = "{}/{}-input.sock".format(Parametres().parametre(Cles.CHEMIN_SOCKETS_DOM0), self.domaine_gui)
        self.journal.debug("Ouvre le canal avec la socket Xenbus {} pour le domaine {}".format(chemin_fichier, self.domaine_gui))

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:            
            sock.connect(chemin_fichier)
            self.socket_gui = sock
            return True
        except:
            self.journal.warn("La socket {} n'a pas pu être ouverte".format(chemin_fichier))
            return False
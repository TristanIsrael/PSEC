import threading, time, glob, socket, os
from . import MqttClient, Logger, Parametres, Cles, Domaine, SingletonMeta

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

    sys_gui_socket = None
    sys_usb_socket = None
    domaine_gui = Domaine.INDEFINI

    def __init__(self, client_log:MqttClient):
        Logger().setup("IO Proxy", client_log)

    def demarre(self):
        Logger().info("Starting I/O proxy")

        # On vérifie qu'un domaine GUI a bien été défini
        self.domaine_gui = Parametres().parametre(Cles.NOM_DOMAINE_GUI)
        if self.domaine_gui == None:
            Logger().warn("No GUI domain defined, cancel.")
            return        
        
        threading.Thread(target=self.__monitor_gui_io_socket).start()
        threading.Thread(target=self.__monitor_usb_io_socket).start()        
        
    def __monitor_gui_io_socket(self):       
        Logger().debug("Start monitoring GUI I/O socket") 

        while True:            
            if self.sys_gui_socket is not None:
                # The socket is already opened
                time.sleep(1)
                continue            

            if not self.__ouvre_socket_gui():
                Logger().warn("The I/O socket with GUI domain could not be opened.")
                time.sleep(1)
                continue

    def __monitor_usb_io_socket(self):
        Logger().debug("Start monitoring USB I/O socket") 

        chemin_socket_usb = Parametres().parametre(Cles.CHEMIN_SOCKET_INPUT_DOM0)
        while True:
            if self.sys_usb_socket is not None:
                # A connexion already exists
                time.sleep(1)
                continue

            if self.sys_gui_socket is None:
                Logger().debug("... wait for GUI I/O socket to be ready")
                time.sleep(1)
                continue

            if not os.path.exists(chemin_socket_usb):
                Logger().warn("... The socket file {} does not exist".format(chemin_socket_usb))
                time.sleep(1)
                continue
            else:
                threading.Thread(target=self.__ecoute_socket_vm_sys_usb, args=(chemin_socket_usb,)).start()
                time.sleep(1)

    ##
    # Fonctions privées
    #
    def __ecoute_socket_vm_sys_usb(self, fichier_socket):
        #Ouvre le flux avec la socket
        Logger().debug("Open the I/O socket {} with DomD sys-usb".format(fichier_socket))

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:            
            sock.connect(fichier_socket)  
            self.sys_usb_socket = sock
            Logger().debug("The I/O socket is opened with DomD sys-usb")
            #recv_buffer = bytearray()

            while(True):
                data = sock.recv(128)

                if data:
                    #Logger().debug("Données reçues depuis le Xenbus : {0}".format(data))                    
                    # On recopie directement sur le port de la GUI
                    try:
                        self.sys_gui_socket.send(data)
                    except:
                        Logger().error("Connection error with GUI I/O socket")
                        self.sys_gui_socket = None
                        return
                        
        except socket.error:
            Logger().error("Could not open connection with I/O socket {}".format(fichier_socket))
            Logger().error(socket.error.strerror) 
            self.sys_usb_socket = None

    def __ouvre_socket_gui(self):
        #Ouvre le flux avec la socket
        chemin_fichier = "{}/{}-input.sock".format(Parametres().parametre(Cles.CHEMIN_SOCKETS_DOM0), self.domaine_gui)
        Logger().debug("Open I/O socket {} to domain {}".format(chemin_fichier, self.domaine_gui))

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:            
            sock.connect(chemin_fichier)
            Logger().debug("The I/O socket is opened with GUI domain")
            self.sys_gui_socket = sock
            return True
        except:
            Logger().warn("The I/O socket {} could not be opened".format(chemin_fichier))
            self.sys_gui_socket = None
            return False
from panoptiscan import Api, Constantes, NotificationFactory, MessagerieDomu, MessagerieDom0, Parametres, Cles, ControleurDom0
import logging, os, socket, threading, time

class TestAPIDomu():
    """ Ce classe permet de tester le fonctionnement de l'API du DomU

    Le test correspond à un test de bout-en-bout mettant en oeuvre tous les mécanismes de 
    communication sur la chaine [DomU]processus -> [DomU]api -> [DomU]socket -> [DomU]messagerie
    -> [Dom0]messagerie -> [Dom0]contrôleur dans les deux sens.

    Les sockets utilisées sont :
    - Test <-> API : pas de socket
    - API <-> Messagerie DomU : socket locale créée par le DomU (/tmp/local.sock)
    - Messagerie DomU <-> Messagerie Dom0 : socket Xenbus (/tmp/xenbus_domu.sock)
    - Messagerie Dom0 <-> Contrôleur Dom0 : pas de socket
    """

    api = None
    logger = None
    socket_xenbus = None

    def __init__(self):
        logging.basicConfig(format=Constantes().constante("format_chaine_log_debug"), level=logging.DEBUG)           
        self.logger = logging.getLogger(__name__)
        self.api = Api(self.__callback_fn)

    def exec(self):        
        chemin_socket_xenbus = Parametres().parametre(Cles.CHEMIN_SOCKET_XENBUS_DOMU)
        self.logger.info("Crée la socket Xenbus pour le test sur {}".format(chemin_socket_xenbus))
        assert(chemin_socket_xenbus != None)
        if os.path.exists(chemin_socket_xenbus):
            os.unlink(chemin_socket_xenbus)

        self.socket_xenbus = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)   
        self.socket_xenbus.bind(chemin_socket_xenbus)
        threading.Thread(target=self.__attend_connexion_xenbus).start()

        self.logger.info("Démarre la messagerie DomU")
        MessagerieDomu().demarre()
        time.sleep(1) # Laisse le temps à la socket d'être prête

        self.logger.info("Démarre la messagerie Dom0")
        MessagerieDom0().demarre()
        time.sleep(1)

        self.logger.info("Démarre le contrôleur Dom0")
        ControleurDom0().demarre()

        self.logger.info("Connecte l'API")
        self.api.connecte_socket()

        msg = NotificationFactory.cree_notification_domu_pret()
        self.api.envoie_message(msg)

    def __callback_fn(self, message):
        self.logger.debug("Message reçu : {}", message.to_json())

    def __attend_connexion_xenbus(self):
        while True:
            self.socket_xenbus.listen(10)
            connexion, _ = self.socket_xenbus.accept()
            self.logger.debug("Echange en cours sur le Xenbus")
            threading.Thread(target=self.__ecoute_connexion_xenbus, args=(connexion,)).start()

    def __ecoute_connexion_xenbus(self, connexion):
         while True:
            data = connexion.recv(Parametres().parametre(Cles.TAILLE_TRAME))
            if data:
                self.logger.debug("Données reçues depuis la socket Xenbus : %s" % data)                

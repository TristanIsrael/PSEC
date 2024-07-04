from panoptiscan import Parametres, Cles, MessagerieDomu, NotificationHelper, Constantes
import threading, socket, os, logging

class TestMessagerieDomu():
    """ Cette classe permet de tester le fonctionne de la messagerie du Dom0

    Les tests réalisés permettent de :
    - Valider la bonne réception des message sur plusieurs sockets DomU
    - Valider la bonne interprétation des messages
    - Valider le fonctionnement de la notification etat_domu 
    """
    
    sockets_xenbus = {}
    step = 1    
    logger = None

    def __init__(self):                
        logging.basicConfig(format=Constantes().constante("format_chaine_log_debug"), level=logging.DEBUG)           
        self.logger = logging.getLogger(__name__)      
        Parametres().set_fichier_parametres( os.path.dirname(__file__) +"/configtest.conf" )                

    def exec(self):     
        logging.info("Démarrage des tests")        
        self.testcase_1()        
        
    # Ce cas de test met en oeuvre un échange de messages entre le Dom0 et un DomU
    # Il est initié du côté DomU. 
    # Le test porte donc sur la partie DomU
    def testcase_1(self):
        # On créé d'abord une socket Xenbus        
        self.logger.info("Crée la socket Xenbus pour le test sur %s" % self.chemin_socket_xenbus)
        assert(self.chemin_socket_xenbus != None)
        if os.path.exists(self.chemin_socket_xenbus):
            os.unlink(self.chemin_socket_xenbus)

        self.socket_xenbus = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)   
        self.socket_xenbus.bind(self.chemin_socket_xenbus)
        threading.Thread(target=self._attend_connexion_xenbus).start()

        # Ainsi qu'une socket locale
        MessagerieDomu().demarre()

    def _attend_connexion_xenbus(self):                
        while True:
            self.socket_xenbus.listen(10)
            connexion, _ = self.socket_xenbus.accept()
            self.logger.info("Connexion reçue sur la socket Xenbus")
            threading.Thread(target=self._lit_socket_xenbus, args=(connexion,)).start()    

            # Une fois la connexion obtenu on commence les tests
            self._testcase_messagerie_domu_1(connexion)

    def _lit_socket_xenbus(self, connexion):
        while(True):
            data = connexion.recv(Parametres().parametre(Cles.TAILLE_TRAME))            
            if data:
                self.logger.info("Données reçues sur le Xenbus : %s" % data.decode())
                if self.step == 1:                        
                    #TODO
                    pass
                elif self.step == 2:
                    assert(data == b"Bonjour socket")

    def _testcase_messagerie_domu_1(self, connexion):
        # Ecriture d'une trame sur la socket xenbus locale
        notif = NotificationHelper.notification_domu_pret()
        connexion.send(notif.to_json().encode())
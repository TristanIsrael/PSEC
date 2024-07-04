from panoptiscan import Parametres, Cles, ControleurDom0, NotificationFactory, Constantes
import threading, socket, os, logging, json

class TestMessagerieDom0():
    chemin_socket_xenbus = None
    etape = 1    
    logger = None
    socket_buffers = {}
    compteur_etape1 = 0

    def __init__(self):                
        logging.basicConfig(format=Constantes().constante("format_chaine_log_debug"), level=logging.DEBUG)           
        self.logger = logging.getLogger(__name__)
        #logging.basicConfig(level=logging.DEBUG)        
        Parametres().set_fichier_parametres( os.path.dirname(__file__) +"/configtest.conf" )                

    def exec(self):     
        logging.info("Démarrage des tests")
        self.chemin_socket_xenbus = Parametres().parametre(Cles.CHEMIN_SOCKET_XENBUS_DOMU) 
        self.testcase_messagerie_domu()        
        
    # Ce cas de test met en oeuvre un échange de messages entre le Dom0 et un DomU
    # Il est initié du côté DomU. 
    # Le test porte donc sur la partie DomU
    def testcase_messagerie_domu(self):
        # On crée autant de sockets Xenbus que nécessaire pour échanger avec les DomU
        for chemin_socket_domu in Parametres().parametre(Cles.CHEMINS_SOCKETS_XENBUS_DOMU):
            self.logger.info("Client DomU déclaré %s" % chemin_socket_domu)
            assert(chemin_socket_domu != None)
            if os.path.exists(chemin_socket_domu):
                os.unlink(chemin_socket_domu)

            socket_xenbus = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)   
            socket_xenbus.bind(chemin_socket_domu)
            threading.Thread(target=self._attend_connexion_xenbus, args=(socket_xenbus,)).start()

        # Ensuite on démarre la messagerie Dom0
        ControleurDom0().demarre()

    def _attend_connexion_xenbus(self, socket_xenbus):                
        while True:
            socket_xenbus.listen(10)
            connexion, _ = socket_xenbus.accept()
            self.logger.info("Connexion reçue sur la socket Xenbus")
            threading.Thread(target=self._lit_socket_xenbus, args=(connexion,)).start()    

            # Une fois la connexion obtenu on commence les tests
            self.__testcase_1(connexion)

    def _lit_socket_xenbus(self, connexion):
        while(True):
            data = connexion.recv(Parametres().parametre(Cles.TAILLE_TRAME))            
            
            if data:
                self.logger.info("Données reçues sur le Xenbus : %s" % data.decode())
                buf = self.socket_buffers.get(connexion)
                if buf == None:
                    buf = bytearray()
                    self.socket_buffers[connexion] = buf                    

                buf.extend(data)

                if buf.endswith(b'\n'):
                    self.logger.debug("Les données sont complètes")                    
                    
                    if self.etape == 1:      
                        self.logger.info(buf)                  
                        assert buf == b'{"type":"notification","source":"vm_test","destination":"indefini","payload":{"evenement":"etat_domu","data":{"pret":1,"domu":"vm_test"}}}\n'                        
                        self.socket_buffers.clear()
                        self.compteur_etape1 += 1
                        if self.compteur_etape1 == 2:
                            self.logger.info("Etape 1 terminée. Passage à l'étape 2")
                            self.__testcase_2(connexion)
                    elif self.etape == 2:
                        assert(data == b"Bonjour socket")

    def __testcase_1(self, connexion):
        # Dans le test 1 on déclenche une connexion et un envoi de message depuis chaque DomU
        self.logger.info("Démarrage du test 1")

        # Une fois les sockets créées, on envoie la notification etat_domu
        notif = NotificationFactory.cree_notification_domu_pret()
        self.logger.info("Envoi de la notification prêt pour les DomU")
        connexion.send(notif.to_json().encode("utf-8")) 

    def __testcase_2(self, connexion):
        self.etape = 2
        self.logger.info("Fin des tests (pas d'étape 2)")
        exit(0)

    def _cree_socket_domu(self, chemin_socket):
        self.logger.info("Crée une socket DomU %s" % chemin_socket)
        try:
            socket_domu = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)            
            socket_domu.connect(chemin_socket) 
            recv_buffer = bytearray() 

            while(True):
                self.logger.info("Attend des données sur la socket %s" % chemin_socket)
                data = socket_domu.recv(Parametres().parametre(Cles.TAILLE_TRAME))

                if data:
                    self.logger.debug("Données reçues sur la socket DomU {0} : {1}".format(chemin_socket, data))
                    recv_buffer.extend(data)
                    
                    if recv_buffer.endswith(b'\n'):
                        self.logger.debug("Le message est complet")

                        try:
                            # Ensuite on décode le message et on le traite
                            j = json.loads(recv_buffer.decode())
                            self._traite_message_xenbus(j)
                            recv_buffer.clear()
                        except Exception:
                            self.logger.error("Erreur : Le message ne peut pas être décodé.")
                            self.logger.error(recv_buffer.decode())                            
            
        except socket.error:            
            self.logger.error("Impossible d'ouvrir la socket %s" % chemin_socket)
    
    def _traite_message_xenbus(self, data):
        pass
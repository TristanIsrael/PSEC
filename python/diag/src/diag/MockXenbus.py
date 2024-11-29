import os, pty
from serial import Serial
import threading, uuid, socket, tempfile
from psec import Logger

class MockXenbus():
    """ Classe MockXenbus

        Cette classe simule le Xenbus en créant un canal de communication entre une socket de domaine Unix et un
        port série. Les données écrites sur l'un sont copiées sur l'autre.
    """

    socket_unix = None
    #port_serie_serveur = None # Côté client
    port_serie_api = None # Côté API

    def cree_socket_DomU(self):
        print("Création de la socket Unix")

        filename = self.__cree_nom_fichier()
        filepath = "{}/{}".format(tempfile.gettempdir(), filename)

        print("Utilisation du fichier {}".format(filepath))

        if os.path.exists(filepath):
            os.remove(filepath)        

        self.socket_unix = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket_unix.bind(filepath)
        threading.Thread(target=self.__ecoute_socket_unix).start()

        return filename

    def cree_port_serie(self):
        print("Création du port série")
        maitre, esclave = pty.openpty() #open the pseudoterminal
        fd_maitre = os.ttyname(maitre) #translate the slave fd to a filename
        fd_esclave = os.ttyname(esclave) #translate the slave fd to a filename        
        self.port_serie_serveur = Serial(fd_maitre)
        self.port_serie_api = Serial(fd_esclave)

        # Vérification du bon fonctionnement
        self.port_serie_serveur.write("TEST\r\n")
        recu = self.port_serie_api.read_all()
        if recu == "TEST\r\n":
        #if True:
            print("Le port série est prêt sur {}".format(fd_esclave))
            threading.Thread(target=self.__ecoute_port_serie).start()
            return fd_esclave
        else:
            Logger().error("Le port série n'est pas prêt. Reçu={}".format(recu), "MockXenbus")
            return None

    def __cree_nom_fichier(self):
        return uuid.uuid4().hex

    def __ecoute_socket_unix(self):
        while True:
            self.socket_unix.listen(1)
            conn, addr = self.socket_unix.accept()
            datagram = conn.recv(1024)
            if len(datagram) > 0:
                print("Données reçues sur la socket")
                self.__ecrit_port_serie(datagram)

    def __ecoute_port_serie(self):
        while True:
            data = self.port_serie_api.read(1024)
            if len(data) > 0:
                print("Données reçues sur le port série")
                self.__ecrit_socket(data)

    def __ecrit_port_serie(self, data):
        self.port_serie_api.write(data)

    def __ecrit_socket(self, data):
        self.socket_unix.write(data)

if __name__ == '__main__':
    print("Exécution du test du simulateur Xenbus")
    print("")

    mock = MockXenbus()
    filepath_serie = mock.cree_port_serie()
    filepath_sock = mock.cree_socket_DomU()

    assert(filepath_serie != None)
    assert(filepath_sock != None)

    print("Ecriture sur le port série {}".format(filepath_serie))
    client_serie = Serial(filepath_serie)
    client_serie.write(b"Ceci est un test\r\n")
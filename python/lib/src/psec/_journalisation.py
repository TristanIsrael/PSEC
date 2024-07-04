import logging, colorlog, logging.handlers, os, serial, glob, socket, threading, io, time
from logging import StreamHandler
from . import Parametres, Constantes, Cles, SingletonMeta, Domaine

class SerialHandler(StreamHandler):

    def __init__(self, serial):
        StreamHandler.__init__(self, serial)

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(bytes(msg + self.terminator, 'utf-8'))
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)

class Journal:
    """Classe permettant de journaliser des informations de débogage et de fonctionnement général
    
    Le Journal fonctionne sur le Dom0 et collecte les entrées de journal provenant des DomU depuis 
    les sockets créées par Xen pour chaque Domu.
    """

    niveau = logging.DEBUG    
    domaine = Domaine.INDEFINI
    entite = __name__
    logger = None
    port_serie = None
    sockets_domu = {}

    def __init__(self, entite, domaine = Domaine.INDEFINI):                
        self.domaine = domaine
        self.entite = entite
        
        # Initialisation des paramètres par défaut
        niv = Parametres().parametre(Cles.NIVEAU_JOURNAL)
        if niv != None:            
            self.niveau = niv
        
        domaine = Parametres().parametre(Cles.IDENTIFIANT_DOMAINE)
        if domaine != None:
            self.domaine = domaine

        # Initialisation du logger        
        self.logger = logging.getLogger(self.entite)
        
        # Si on est sur un DomU
        # Lors de l'instanciation il faut ouvrir la connexion série avec le port 
        # de communication dédié à la journalisation (Cles.CHEMIN_PORT_JOURNAL_DOMU)
        if domaine != None and domaine != Domaine.DOM0:
            try:
                chemin_port = Parametres().parametre(Cles.CHEMIN_PORT_JOURNAL_DOMU)
                self.port_serie = serial.Serial(port= chemin_port)
            
                # Ajout du Hangler série
                serial_handler = SerialHandler(self.port_serie)        
                self.logger.addHandler(serial_handler)
            except serial.SerialException as e:
                self.logger.error("Impossible d'ouvrir la connexion avec le port de journalisation sur {}".format(chemin_port))
                self.logger.error(e)

        # Handler Stdout
        stdout_handler = logging.StreamHandler()        
        self.logger.addHandler(stdout_handler)    

        # Handler fichier
        fichier_handler = logging.FileHandler(Parametres().parametre(Cles.CHEMIN_JOURNAL_LOCAL), "a", "utf-8")
        if Parametres().parametre(Cles.ACTIVE_JOURNAL_LOCAL):
            self.logger.addHandler(fichier_handler)
        
        self.logger = logging.LoggerAdapter(self.logger, {'domaine': Parametres().parametre(Cles.IDENTIFIANT_DOMAINE)})

        # Gestion du format de la log
        if self.niveau < logging.INFO:
            format_chaine_log = logging.Formatter(Parametres().parametre("format_chaine_log_debug"))
        else:
            format_chaine_log = logging.Formatter(Parametres().parametre("format_chaine_log_prod"))        
        stdout_handler.setFormatter(format_chaine_log)
        fichier_handler.setFormatter(format_chaine_log)
        
        if domaine != None and domaine != Domaine.DOM0:
            try:
                serial_handler.setFormatter(format_chaine_log)
            except Exception:
                self.logger.info("Le handler série n'est pas instancié")

        self.logger.setLevel(self.niveau)
        #self.logger.info("Le niveau de log est {}".format(Parametres.niveau_journalisation_to_string(self.niveau)))

    def get_niveau_journalisation(self):
        return self.niveau    
    
    def set_niveau_journalisation(self, niveau):
        self.niveau = niveau

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warn(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

class JournalProxy():
    """Cette classe permet au Dom0 de gérer les journaux provenant des DomU
    
    Elle est instanciée par un démon qui a pour objectif d'alimenter le journal des événéments avec
    les entrées en provenance des différents DomU.
    """

    sockets_domu = []
    journal = None
    fichier_log = None
    verrou_fichier = threading.Lock()

    def __init__(self):
        self.journal = Journal("JournalProxy")
        
        # On ouvre le fichier de logs local
        self.__ouvre_fichier_log()        

    def demarre(self):
        self.__verifie_sockets()

    ###
    # Fonctions privées
    #
    def __ouvre_fichier_log(self):
        try:
            chemin = Parametres().parametre(Cles.CHEMIN_JOURNAL_LOCAL)            
            self.fichier_log = io.open(chemin, "a")
        except Exception as e:
            self.journal.error("Impossible d'ouvrir le fichier journal {}".format(chemin))
            self.journal.error(e)

    def __chemin_sockets(self):
        return "{}/*-log.sock".format(Parametres().parametre(Cles.CHEMIN_SOCKETS_JOURNAL))

    def __verifie_sockets(self):
        chemin = self.__chemin_sockets()
        self.journal.info("Vérification des sockets de journalisation DomU")
        self.journal.debug("Chemin des sockets : {}".format(chemin))

        while True:
            fichiers = glob.glob(chemin)
            if len(fichiers) == 0:
                self.journal.debug("Aucune socket de journal n'est ouverte actuellement")

            for f in fichiers:                
                self.journal.debug("Connexion à la socket de journal {}".format(f))
                socket = self.__connecte_socket_log(f)

                if f not in self.sockets_domu:
                    self.sockets_domu[f] = socket
                    if socket != None:       
                        thread = threading.Thread(target=self.__attend_donnees_log, args=(socket,))
                        thread.start()

            time.sleep(5)

    def __connecte_socket_log(self, chemin):
        self.journal.debug("Connexion à la socket de journal {}".format(chemin))

        try:
            socket_xenbus = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)            
            socket_xenbus.connect(chemin) 
        except Exception as e:
            self.journal.error("La connexion à la socket n'a pu être établie")
            self.journal.error(e)
            return None

        return socket_xenbus

    def __attend_donnees_log(self, socket):
        self.journal.debug("Attend des données sur la socket {}".format(socket))

        while(True):
            data = socket.recv(Parametres().parametre(Cles.TAILLE_TRAME))

            if data:
                # On a reçu des données, il faut maintenant les ajouter au fichier journal
                # Il faut travailler dans une section critique pour éviter les conflits d'écriture
                # et les mélanges dans les logs
                self.verrou_fichier.acquire()
                if self.fichier_log.closed:
                    self.__ouvre_fichier_log()
                self.fichier_log.write(data)
                self.verrou_fichier.release()
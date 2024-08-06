from . import SingletonMeta

class Cles: 
    NIVEAU_JOURNAL = "niveau_debug"
    CHEMIN_JOURNAL = "chemin_journal"
    CHEMIN_JOURNAL_LOCAL = "chemin_journal_local"
    IDENTIFIANT_DOMAINE = "identifiant_domaine"
    CHEMIN_SOCKET_MSG = "chemin_socket_msg"
    CHEMIN_SOCKET_INPUT_DOMU = "chemin_socket_input_domu"
    CHEMIN_SOCKET_INPUT_DOM0 = "chemin_socket_input_dom0"
    CHEMIN_SOCKETS_JOURNAL = "chemin_sockets_log"
    CHEMIN_SOCKETS_MESSAGERIE = "chemin_sockets_msg"
    CHEMIN_SOCKETS_DOM0 = "chemin_sockets_dom0"
    #CHEMIN_SOCKET_API = "chemin_socket_api"
    #CHEMIN_FICHIER_CONFIG_LOCAL = "chemin_fichier_config_local"
    CHEMIN_FICHIER_CONFIG_GLOBAL = "chemin_fichier_config_global"        
    TAILLE_TRAME = "taille_trame"
    CHEMIN_PORT_JOURNAL_DOMU = "chemin_port_journal_domu"        
    CHEMIN_FICHIERS_PID = "chemin_fichiers_pid"
    CHEMIN_MONTAGE_USB = "chemin_montage_usb"
    DEPOT_LOCAL = "depot_local"
    ACTIVE_JOURNAL_LOCAL = "active_journal_local"
    NOM_DOMAINE_GUI = "nom_domaine_gui"
    BENCHMARK_INPUTS_ITERATIONS = "benchmark_inputs_iterations"
    CHEMIN_DEPOT_DOM0 = "chemin_depot_dom0"
    CHEMIN_DEPOT_DOMU = "chemin_depot_domu"

class EtatDomu:
    INCONNU = 0
    DEMARRE = 1
    ARRETE = 2

class EtatDisque:
    INCONNU = "inconnu"
    PRESENT = "présent"
    ABSENT = "absent"

class EtatFichier:
     DISPONIBLE = "disponible"
     ERREUR = "erreur"
     COPIE = "copié"
     SUPPRIME = "supprimé"

class Domaine:
    """Classe définissant le type de domaine (DomU ou Dom0)"""
    INDEFINI = "indefini"
    DOM0 = "Dom0"
    SYS_USB = "sys-usb"
    GUI = "gui"
    TOUS = "tous"

class TypeEntree():
    INDEFINI = "indefini"
    SOURIS = "souris"
    CLAVIER = "clavier"
    TACTILE = "tactile"

class BoutonSouris():
    AUCUN = 0
    GAUCHE = 1
    MILIEU = 2
    DROIT = 3

class BenchmarkId():
    INPUTS = "inputs"
    FILES = "files"

class Constantes(metaclass=SingletonMeta):
    """Classe définissant des constantes pour le système"""    

    constantes = {
        Cles.CHEMIN_FICHIER_CONFIG_GLOBAL: "/etc/psec/global.conf",        
        # Sockets pv channel entre Dom0 et DomU
        Cles.CHEMIN_SOCKET_MSG: "/dev/hvc1",
        Cles.CHEMIN_SOCKET_INPUT_DOMU: "/dev/hvc3",
        #Cles.CHEMIN_SOCKET_API: "/run/panoptiscan.sock",
        Cles.TAILLE_TRAME: 1024,
        # Journalisations
        Cles.CHEMIN_JOURNAL_LOCAL: "/var/log/psec/psec.log",
        "format_chaine_log_prod": '%(asctime)s %(levelname)-8s %(domaine)-10s [%(name)-20s] %(message)s',
        "format_chaine_log_debug": '%(asctime)s %(levelname)-8s %(domaine)-10s [%(name)-20s] %(message)s',
        Cles.CHEMIN_PORT_JOURNAL_DOMU: "/dev/hvc2",
        Cles.CHEMIN_SOCKETS_JOURNAL: "/var/run",
        Cles.CHEMIN_SOCKETS_MESSAGERIE: "/var/run",
        Cles.CHEMIN_SOCKETS_DOM0: "/var/run",
        Cles.CHEMIN_SOCKET_INPUT_DOM0: "/var/run/sys-usb-input.sock",
        Cles.CHEMIN_FICHIERS_PID: "/tmp",        
        Cles.CHEMIN_MONTAGE_USB: "/media/usb", #/mnt
        Cles.DEPOT_LOCAL: "depot_local",
        Cles.ACTIVE_JOURNAL_LOCAL: True,
        "chemin_fichier_config_global": "/etc/psec/global.conf",
        Cles.NOM_DOMAINE_GUI: "sys-gui",
        Cles.BENCHMARK_INPUTS_ITERATIONS: 1000,
        Cles.CHEMIN_DEPOT_DOM0: "/usr/lib/psec/storage",
        Cles.CHEMIN_DEPOT_DOMU: "/mnt/storage"
    }                

    def constante(self, cle):
        valeur = self.constantes.get(cle)
        if valeur:
            return valeur
        else:
            return None
        
    REPOSITORY = "__repository__"
    FOOTPRINT_METHOD = "md5"
from . import SingletonMeta

class Cles: 
    NIVEAU_JOURNAL = "niveau_debug"
    CHEMIN_JOURNAL = "chemin_journal"
    CHEMIN_JOURNAL_LOCAL = "chemin_journal_local"
    IDENTIFIANT_DOMAINE = "identifiant_domaine"
    CHEMIN_SOCKET_INPUT_DOMU = "chemin_socket_input_domu"
    CHEMIN_SOCKET_INPUT_DOM0 = "chemin_socket_input_dom0"
    CHEMIN_SOCKETS_JOURNAL = "chemin_sockets_log"     
    CHEMIN_SOCKETS_MESSAGERIE = "chemin_sockets_msg"    
    #CHEMIN_SOCKET_API = "chemin_socket_api"
    #CHEMIN_FICHIER_CONFIG_LOCAL = "chemin_fichier_config_local"
    CHEMIN_FICHIER_CONFIG_GLOBAL = "chemin_fichier_config_global"        
    TAILLE_TRAME = "taille_trame"    
    CHEMIN_FICHIERS_PID = "chemin_fichiers_pid"
    CHEMIN_MONTAGE_USB = "chemin_montage_usb"
    DEPOT_LOCAL = "depot_local"
    ACTIVE_JOURNAL_LOCAL = "active_journal_local"
    NOM_DOMAINE_GUI = "nom_domaine_gui"
    BENCHMARK_INPUTS_ITERATIONS = "benchmark_inputs_iterations"
    CHEMIN_DEPOT_DOM0 = "chemin_depot_dom0"        

    SERIAL_PORT_MSG = "serial_port_msg"
    SERIAL_PORT_LOG = "serial_port_log"
    MQTT_MSG_BROKER_SOCKET = "mqtt_msg_broker_socket"    
    MQTT_MSG_BROKER_SOCKETS = "mqtt_msg_broker_sockets"    
    MQTT_LOG_BROKER_SOCKET = "mqtt_log_broker_socket"
    MQTT_MSG_SOCKET_FILTER = "mqtt_msg_socket_filter"
    MQTT_LOG_SOCKET_FILTER = "mqtt_log_socket_filter"
    XEN_SOCKETS_PATH = "xen_sockets_path"
    STORAGE_PATH_DOMU = "storage_path_domu"

class TypeEntree:
    INCONNU = 0
    CLAVIER = 1
    SOURIS = 2
    TOUCH = 3

class BoutonSouris():
    AUCUN = 0
    GAUCHE = 1
    MILIEU = 2
    DROIT = 3

class BenchmarkId():
    INPUTS = "inputs"
    FILES = "files"

class EtatComposant():
    UNKNOWN = "unknown"
    STARTING = "starting"
    READY = "ready"
    ERROR = "error"

class Constantes(metaclass=SingletonMeta):
    """Classe définissant des constantes pour le système"""        

    constantes = {
        Cles.SERIAL_PORT_MSG: "/dev/hvc1",
        Cles.SERIAL_PORT_LOG: "/dev/hvc2",
        Cles.MQTT_MSG_BROKER_SOCKET: "/tmp/mqtt_msg_dom0.sock",
        Cles.MQTT_MSG_BROKER_SOCKETS: "/tmp/mqtt_msg*.sock",
        Cles.MQTT_LOG_BROKER_SOCKET: "/tmp/mqtt_log.sock",
        Cles.MQTT_MSG_SOCKET_FILTER: "/var/run/*-msg.sock",
        Cles.MQTT_LOG_SOCKET_FILTER: "/var/run/*-log.sock",
        Cles.XEN_SOCKETS_PATH: "/var/run",

        Cles.CHEMIN_FICHIER_CONFIG_GLOBAL: "/etc/psec/global.conf",        
        # Sockets pv channel entre Dom0 et DomU        
        Cles.CHEMIN_SOCKET_INPUT_DOMU: "/dev/hvc2",
        #Cles.CHEMIN_SOCKET_API: "/run/panoptiscan.sock",
        Cles.TAILLE_TRAME: 1024,
        # Journalisations
        Cles.CHEMIN_JOURNAL_LOCAL: "/var/log/psec/psec.log",
        "format_chaine_log_prod": '%(asctime)s %(levelname)-8s %(domaine)-10s [%(entite)-20s] %(message)s',
        "format_chaine_log_debug": '%(asctime)s %(levelname)-8s %(domaine)-10s [%(entite)-20s] %(message)s',        
        #Cles.CHEMIN_SOCKETS_JOURNAL: "/var/run",
        #Cles.CHEMIN_SOCKETS_MESSAGERIE: "/var/run",
        #Cles.CHEMIN_SOCKETS_DOM0: "/var/run",
        Cles.CHEMIN_SOCKET_INPUT_DOM0: "/var/run/sys-usb-input.sock",
        Cles.CHEMIN_FICHIERS_PID: "/tmp",        
        Cles.CHEMIN_MONTAGE_USB: "/media/usb", #/mnt
        Cles.DEPOT_LOCAL: "depot_local",
        Cles.ACTIVE_JOURNAL_LOCAL: True,
        "chemin_fichier_config_global": "/etc/psec/global.conf",
        Cles.NOM_DOMAINE_GUI: "sys-gui",
        Cles.BENCHMARK_INPUTS_ITERATIONS: 1000,
        Cles.CHEMIN_DEPOT_DOM0: "/usr/lib/psec/storage",
        Cles.STORAGE_PATH_DOMU: "/mnt/storage"
    }                

    def constante(self, cle):
        valeur = self.constantes.get(cle)
        if valeur:
            return valeur
        else:
            return None
        
    REPOSITORY = "__repository__"
    FOOTPRINT_METHOD = "md5"
    PSEC_DISK_CONTROLLER = "psec_disk_controller"
    PSEC_INPUT_CONTROLLER = "psec_input_controller"
    PSEC_IO_BENCHMARK = "psec_io_benchmark"
    PSEC_SYSTEM_CONTROLLER = "psec_system_controller"

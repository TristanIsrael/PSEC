from enum import Enum, auto
from . import SingletonMeta

class Keys(Enum):
    LOG_LEVEL = auto()
    LOG_PATH = auto()
    LOCAL_LOG_PATH = auto()
    DOMAIN_ID = auto()
    INPUT_SOCKET_PATH_DOMU = auto()
    INPUT_SOCKET_PATH_DOM0 = auto()
    INPUT_SOCKET_LOG = auto()
    INPUT_SOCKET_MESSAGING = auto()
    GLOBAL_CONFIG_FILE = auto()
    USB_MOUNT_PATH = auto()
    LOCAL_REPOSITORY = auto()
    ACTIVATE_LOCAL_LOG = auto()
    GUI_DOMAIN_NAME = auto()
    BENCHMARK_INPUTS_ITERATIONS = auto()
    LOCAL_REPOSITORY_DOM0 = auto()
    SERIAL_PORT_MSG = auto()
    SERIAL_PORT_LOG = auto()
    MQTT_MSG_BROKER_SOCKET = auto()
    MQTT_MSG_BROKER_SOCKETS = auto()
    MQTT_LOG_BROKER_SOCKET = auto()
    MQTT_MSG_SOCKET_FILTER = auto()
    MQTT_LOG_SOCKET_FILTER = auto()
    XEN_SOCKETS_PATH = auto()
    STORAGE_PATH_DOMU = auto()
    PID_FILEPATH = auto()

class InputType:
    UNKNOWN = 0
    KEYBOARD = 1
    MOUSE = 2
    TOUCH = 3

class BenchmarkId():
    INPUTS = "inputs"
    FILES = "files"

class ComponentState():
    UNKNOWN = "unknown"
    STARTING = "starting"
    READY = "ready"
    ERROR = "error"

class Constants(metaclass=SingletonMeta):
    """ This class defines constants for PSEC internal usage
    """

    constants = {
        Keys.SERIAL_PORT_MSG: "/dev/hvc1",
        Keys.SERIAL_PORT_LOG: "/dev/hvc2",
        Keys.MQTT_MSG_BROKER_SOCKET: "/tmp/mqtt_msg_dom0.sock",
        Keys.MQTT_MSG_BROKER_SOCKETS: "/tmp/mqtt_msg*.sock",
        Keys.MQTT_LOG_BROKER_SOCKET: "/tmp/mqtt_log.sock",
        Keys.MQTT_MSG_SOCKET_FILTER: "/var/run/*-msg.sock",
        Keys.MQTT_LOG_SOCKET_FILTER: "/var/run/*-log.sock",
        Keys.XEN_SOCKETS_PATH: "/var/run",
        Keys.GLOBAL_CONFIG_FILE: "/etc/psec/global.conf",
        Keys.INPUT_SOCKET_PATH_DOMU: "/dev/hvc2",
        # Journalisations
        Keys.LOCAL_LOG_PATH: "/var/log/psec/psec.log",
        "production_log_string_format": '%(asctime)s %(levelname)-8s %(domaine)-10s [%(entite)-20s] %(message)s',
        "debug_log_string_format": '%(asctime)s %(levelname)-8s %(domaine)-10s [%(entite)-20s] %(message)s',
        Keys.INPUT_SOCKET_PATH_DOM0: "/var/run/sys-usb-input.sock",
        Keys.PID_FILEPATH: "/tmp",
        Keys.USB_MOUNT_PATH: "/media/usb",
        Keys.LOCAL_REPOSITORY: "depot_local",
        Keys.ACTIVATE_LOCAL_LOG: True,
        "global_config_file": "/etc/psec/global.conf",
        Keys.GUI_DOMAIN_NAME: "sys-gui",
        Keys.BENCHMARK_INPUTS_ITERATIONS: 1000,
        Keys.LOCAL_REPOSITORY_DOM0: "/usr/lib/psec/storage",
        Keys.STORAGE_PATH_DOMU: "/mnt/storage"
    }                

    def constant(self, cle):
        valeur = self.constants.get(cle)
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

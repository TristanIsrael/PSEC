""" \author Tristan Israël """

from enum import Enum

class InputType:
    UNKNOWN = 0
    KEYBOARD = 1
    MOUSE = 2
    TOUCH = 3

class BenchmarkId:
    INPUTS = "inputs"
    FILES = "files"

class ComponentState(Enum):
    UNKNOWN = "unknown"
    STARTING = "starting"
    READY = "ready"
    ERROR = "error"

class Constants():
    """ This class defined constants for the whole system """        

    SERIAL_PORT_MSG = "/dev/hvc1"
    SERIAL_PORT_LOG = "/dev/hvc2"
    MQTT_MSG_BROKER_SOCKET = "/tmp/mqtt_msg_dom0.sock"
    MQTT_MSG_BROKER_SOCKETS = "/tmp/mqtt_msg*.sock"
    MQTT_LOG_BROKER_SOCKET = "/tmp/mqtt_log.sock"
    MQTT_MSG_SOCKET_FILTER = "/var/run/*-msg.sock"
    MQTT_LOG_SOCKET_FILTER = "/var/run/*-log.sock"
    XEN_SOCKETS_PATH = "/var/run"

    # PV channel socket between DomU and Dom0
    DOMU_INPUT_SOCKET_FILEPATH = "/dev/hvc2"
    FRAME_SIZE = 1024    
    LOCAL_LOG_FILEPATH = "/var/log/safecor/safecor.log"
    LOG_STRING_FORMAT_PRODUCTION = '%(asctime)s %(levelname)-8s %(domaine)-10s [%(entite)-20s] %(message)s'
    LOG_STRING_FORMAT_DEBUG = '%(asctime)s %(levelname)-8s %(domaine)-10s [%(entite)-20s] %(message)s'
    SYS_USB_INPUT_SOCKET_FILEPATH = "/var/run/sys-usb-input.sock"
    PID_FILES_PATH = "/tmp"
    USB_MOUNT_POINT = "/media/usb" #/mnt
    ENABLE_LOCAL_LOG = True
    GUI_DOMAIN_NAME = "sys-gui"
    BENCHMARK_INPUTS_ITERATIONS = 1000
    DOM0_REPOSITORY_PATH = "/usr/lib/safecor/storage"
    DOMU_REPOSITORY_PATH = "/mnt/storage"
        
    STR_REPOSITORY = "__repository__"
    FINGERPRINT_METHOD = "md5"
    STR_SAFECOR_DISK_CONTROLLER = "safecor_disk_controller"
    STR_SAFECOR_INPUT_CONTROLLER = "safecor_input_controller"
    STR_IO_BENCHMARK = "safecor_io_benchmark"
    STR_SAFECOR_SYSTEM_CONTROLLER = "safecor_system_controller"

__author__ = "Tristan Israël (tristan.israel@alefbet.net)"
__version__ = '1.2.0'

from ._singleton import SingletonMeta
from ._constantes import Constantes, Cles, BoutonSouris, InputType, BenchmarkId, EtatComposant
from ._system import System
try:
    from ._keymap_fr import KeymapFR
except Exception as e:
    print("The class KeymapFR won't be available due to missing dependancy")
    print(e)
from ._topics import Topics
from ._mqtt_helper import MqttHelper
from ._mqtt_client import MqttClient, ConnectionType, SerialMQTTClient
from ._parametres import Parametres
from ._request_factory import RequestFactory
from ._notification_factory import NotificationFactory
from ._logger import Logger
from ._fichier_helper import FichierHelper
from ._response_factory import ResponseFactory
try:
    from ._disk_monitor import DiskMonitor
except Exception as e:
    print("The class DiskMonitor won't be available due to missing dependancy")
    print(e)
from ._mouse import Mouse, MouseButton, MouseWheel, MouseMove
from ._tasks_runner import TaskRunner
try:
    from ._demon_inputs import InputsDaemon
except Exception as e:
    print("The classes DemonInputs, ControleurVmSysUsb et ControleurBenchmark won't be available due to missing dependancy")
    print(e)
try:
    from ._sys_usb_controller import SysUsbController
except Exception as e:
    print("The class SysUsbController won't be available due to missing dependancy")
#from ._inputs_proxy import InputsProxy
from ._dom0_controller import Dom0Controller
from ._components_helper import ComponentsHelper
from ._mqtt_factory import MqttFactory
from ._api import Api
from ._mock_sys_usb_controller import MockSysUsbController
from ._debugging import Debugging

import logging
from logging import NullHandler

__all__ = [
    "__version__",
    "KeymapFR",
    "InputType", "BoutonSouris", "Constantes", "EtatComposant", "MouseMove",     
    "RequestFactory",
    #"Journal", "JournalProxy", "DemonProxyJournal",
    "Logger",
    "NotificationFactory", "BoutonSouris",
    "Parametres", "Cles", "ResponseFactory",    
    "DiskMonitor",
    "FichierHelper",    
    "SingletonMeta",
    "InputsDaemon",
    "Mouse", "MouseButton", "MouseWheel", #"InputsProxy",
    #"ControleurBenchmark", 
    "BenchmarkId",
    #"MockXenbus",
    "TaskRunner",
    "MqttClient", "ConnectionType", "Topics", "MqttFactory", "SerialMQTTClient", "MqttHelper",
    "Dom0Controller", "SysUsbController", "Api",
    "ComponentsHelper",
    "MockSysUsbController",
    "System", "Debugging"
]

logging.getLogger(__name__).addHandler(NullHandler())
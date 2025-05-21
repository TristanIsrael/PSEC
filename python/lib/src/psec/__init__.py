__author__ = "Tristan Israël (tristan.israel@alefbet.net)"
__version__ = '1.1'

import logging
from logging import NullHandler

from ._singleton import SingletonMeta
from ._system import System
from ._constants import Constants, Keys, InputType, BenchmarkId, ComponentState
try:
    from ._keymap_fr import KeymapFR
except Exception as e:
    print("The class KeymapFR won't be available due to missing dependancy")
    print(e)
from ._topics import Topics
from ._mqtt_helper import MqttHelper
from ._mqtt_client import MqttClient, ConnectionType, SerialMQTTClient
#from .deprecated._parameters import Parameters
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
    from ._demon_inputs import DemonInputs
except Exception as e:
    print("The classes DemonInputs, ControleurVmSysUsb et ControleurBenchmark won't be available due to missing dependancy")
    print(e)
try:
    from ._sys_usb_controller import SysUsbController
except Exception as e:
    print("The class SysUsbController won't be available due to missing dependancy")
from ._api import Api
from ._dom0_controller import Dom0Controller
from ._components_helper import ComponentsHelper
from ._mqtt_factory import MqttFactory
from ._mock_sys_usb_controller import MockSysUsbController


__all__ = [
    "__version__",
    "KeymapFR",
    "InputType", "MouseButton", "Constants", "ComponentState", "MouseMove",     
    "RequestFactory",
    "Logger",
    "NotificationFactory", "MouseButton",
    "Keys", "ResponseFactory",    
    #"Parameters"
    "DiskMonitor",
    "FichierHelper",    
    "SingletonMeta",
    "DemonInputs",
    "Mouse", "MouseButton", "MouseWheel",
    "BenchmarkId",
    "TaskRunner",
    "MqttClient", "ConnectionType", "Topics", "MqttFactory", "SerialMQTTClient", "MqttHelper",
    "Dom0Controller", "SysUsbController", "Api",
    "ComponentsHelper",
    "MockSysUsbController",
    "System"    
]

logging.getLogger(__name__).addHandler(NullHandler())

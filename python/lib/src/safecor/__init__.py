__author__ = "Tristan Israël (tristan.israel@alefbet.net)"
__version__ = '1.2.0'

from ._topology import Topology, Domain, Screen, DomainType
from ._singleton import SingletonMeta
from ._constants import Constants, MouseButton, InputType, BenchmarkId, ComponentState
from ._libvirt_helper import LibvirtHelper
from ._system import System, topology
try:
    from ._keymap_fr import KeymapFR
except Exception as e:
    print("The class KeymapFR won't be available due to missing dependancy")
    print(e)
from ._topics import Topics
from ._mqtt_helper import MqttHelper
from ._mqtt_client import MqttClient, ConnectionType, SerialMQTTClient
from ._request_factory import RequestFactory
from ._notification_factory import NotificationFactory
from ._logger import Logger
from ._file_helper import FileHelper
from ._response_factory import ResponseFactory
try:
    from ._disk_monitor import DiskMonitor
except Exception as e:
    print("The class DiskMonitor won't be available due to missing dependancy")
    print(e)
from ._mouse import Mouse, MouseButton, MouseWheel, MouseMove
from ._tasks_runner import TaskRunner
from ._inputs_daemon import InputsDaemon
from ._sys_usb_controller import SysUsbController
#from ._inputs_proxy import InputsProxy
from ._dom0_controller import Dom0Controller
from ._components_helper import ComponentsHelper
from ._mqtt_factory import MqttFactory
from ._api import Api
from ._mock_sys_usb_controller import MockSysUsbController
from ._debugging import Debugging
from ._api_helper import ApiHelper
from ._configuration_reader import Configuration, ConfigurationReader

import logging
from logging import NullHandler

__all__ = [
    "__version__",
    "SingletonMeta",
    "Topology", "Domain", "DomainType",
    "Constants", "System", "topology", "Screen", "Constants", "ComponentState",
    "KeymapFR",
    "InputType", 
    "Configuration", "ConfigurationReader",
    "RequestFactory",
    "LibvirtHelper",
    "Logger",
    "NotificationFactory", 
    "ResponseFactory",
    "DiskMonitor",
    "FileHelper",    
    "InputsDaemon",
    "Mouse", "MouseButton", "MouseWheel", "MouseMove",
    "BenchmarkId",
    "TaskRunner",
    "MqttClient", "ConnectionType", "Topics", "MqttFactory", "SerialMQTTClient", "MqttHelper",
    "Dom0Controller", "SysUsbController", "Api",
    "ComponentsHelper",
    "MockSysUsbController",
    "Debugging", "ApiHelper"
]

logging.getLogger(__name__).addHandler(NullHandler())
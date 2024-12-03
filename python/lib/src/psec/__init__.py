from ._singleton import SingletonMeta
from ._constantes import Constantes, Cles, BoutonSouris, TypeEntree, BenchmarkId, EtatComposant
try:
    from ._keymap_fr import KeymapFR
except Exception as e:
    print("La classe KeymapFR ne sera pas disponible")
    print(e)
from ._topics import Topics
from ._mqtt_client import MqttClient, ConnectionType, SerialMQTTClient
from ._logger import Logger
from ._parametres import Parametres, Cles
from ._request_factory import RequestFactory
from ._notification_factory import NotificationFactory
from ._fichier_helper import FichierHelper
from ._response_factory import ResponseFactory
from ._disk_monitor import DiskMonitor
from ._mouse import Mouse, MouseButton, MouseWheel, MouseMove
from ._tasks_runner import TaskRunner
from ._mqtt_factory import MqttFactory
try:
    from ._demon_inputs import DemonInputs          
    from ._controleur_benchmark import ControleurBenchmark  
except Exception as e:
    print("Les classes DemonInputs, ControleurVmSysUsb et ControleurBenchmark ne seront pas disponibles")
    print(e)
from ._api import Api
from ._inputs_proxy import InputsProxy
from ._dom0_controller import Dom0Controller
from ._sys_usb_controller import SysUsbController
from ._mqtt_helper import MqttHelper
from ._components_helper import ComponentsHelper

import logging
from logging import NullHandler

__author__ = "Tristan Israël (tristan.israel@alefbet.net)"
__version__ = '1.0'

__all__ = [
    "KeymapFR",
    "TypeEntree", "BoutonSouris", "Constantes", "EtatComposant", "MouseMove",     
    "RequestFactory",
    #"Journal", "JournalProxy", "DemonProxyJournal",
    "Logger",
    "NotificationFactory", "BoutonSouris",
    "Parametres", "Cles", "ResponseFactory",    
    "DiskMonitor",
    "FichierHelper",    
    "SingletonMeta",
    "DemonInputs",
    "Mouse", "MouseButton", "MouseWheel", "InputsProxy",
    "ControleurBenchmark", "BenchmarkId",
    #"MockXenbus",
    "TaskRunner",
    "MqttClient", "ConnectionType", "Topics", "MqttFactory", "SerialMQTTClient", "MqttHelper",
    "Dom0Controller", "SysUsbController", "Api",
    "ComponentsHelper"
]

logging.getLogger(__name__).addHandler(NullHandler())
from ._singleton import SingletonMeta
from ._constantes import Constantes, Cles, EtatDomu, EtatDisque, Domaine, BoutonSouris, TypeEntree, EtatFichier, BenchmarkId, EtatComposant
try:
    from ._keymap_fr import KeymapFR
except Exception as e:
    print("La classe KeymapFR ne sera pas disponible")
    print(e)
from ._parametres import Parametres, Cles
from ._message import Message, TypeMessage
from ._commande import Commande
from ._erreur_factory import ErreurFactory
from ._journalisation import Journal, JournalProxy
from ._type_evenement import TypeEvenement
from ._type_commande import TypeCommande
from ._type_reponse import TypeReponse
from ._commande_factory import CommandeFactory
from ._notification import Notification
from ._notification_helper import NotificationHelper
from ._notification_factory import NotificationFactory
from ._reponse import Reponse
from ._fichier_helper import FichierHelper
from ._reponse_factory import ReponseFactory
from ._message_helper import MessageHelper
from ._messagerie_domu import MessagerieDomu
from ._messagerie_dom0 import MessagerieDom0
from ._surveillance_disque import SurveillanceDisque
from ._mouse import Mouse, MouseButton, MouseWheel, MouseMove
from ._tasks_runner import TaskRunner
try:
    from ._demon_inputs import DemonInputs          
    from ._controleur_benchmark import ControleurBenchmark  
except Exception as e:
    print("Les classes DemonInputs, ControleurVmSysUsb et ControleurBenchmark ne seront pas disponibles")
    print(e)
from ._api import Api
from ._demon_proxyjournal import DemonProxyJournal
from ._inputs_proxy import InputsProxy
from ._controleur_dom0 import ControleurDom0
from ._mock_xenbus import MockXenbus
from ._controleur_vm_sys_usb import ControleurVmSysUsb

import logging
from logging import NullHandler

__author__ = "Tristan Israël (tristan.israel@alefbet.net)"
__version__ = '1.0'

__all__ = [
    "KeymapFR",
    "Commande", "TypeCommande", "CommandeFactory", "TypeEntree", "BoutonSouris", "EtatFichier", "EtatComposant"
    "Constantes", "EtatDomu", "EtatDisque", "Domaine",
    "ErreurFactory", 
    "Journal", "JournalProxy",
    "Message", "TypeMessage", "MessageHelper", "TypeReponse",
    "Notification",
    "NotificationHelper", "NotificationFactory", "BoutonSouris",
    "MessagerieDom0", "MessagerieDomu", 
    "Parametres", "Cles", "Reponse", "TypeEvenement", "ReponseFactory",
    "ControleurDom0", "Api",
    "SurveillanceDisque",
    "FichierHelper",
    "ControleurVmSysUsb",
    "SingletonMeta",
    "DemonInputs", "DemonProxyJournal",
    "Mouse", "MouseButton", "MouseWheel", "InputsProxy",
    "ControleurBenchmark", "BenchmarkId",
    "MockXenbus",
    "TaskRunner"
]

logging.getLogger(__name__).addHandler(NullHandler())
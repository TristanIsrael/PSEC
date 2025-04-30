from PySide6.QtCore import QObject, Signal
from PySide6.QtCore import QProcess, QTimer, QDir, Property, Slot, QPoint, QCoreApplication, Qt, QEvent, QSize
from PySide6.QtGui import QMouseEvent, QCursor
from PySide6.QtWidgets import QWidget
from psec import Api, Constantes, Topics, BenchmarkId, MqttClient, MqttFactory
import os

class InterfaceSocle(QObject):
    """! Cette classe surveille le XenBus pour échanger des messages avec les autres composants du système.    
    """

    # Member variables
    __disks = []
    #__files = []

    # Signaux
    pret = Signal()
    diskChanged = Signal(str, bool) # nom disque, connecté
    disksChanged = Signal()
    folderChanged = Signal(str)
    filesListReceived = Signal(list)
    #filesChanged = Signal()
    #benchmarkDataChanged = Signal()
    #fileCreated = Signal(str, str, str) # filepath, disk, footprint
    error = Signal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.is_dev_mode = os.getenv("DEVMODE") is not None
        self.mqtt_client = None

    @Slot()
    def start(self, ready_callback):
        print("Starting InterfaceSocle")
        print(f"DEV mode is {"ON" if self.is_dev_mode else "OFF"}")

        if self.is_dev_mode:
            self.mqtt_client = MqttFactory.create_mqtt_network_dev("Diag")
        else:
            self.mqtt_client = MqttFactory.create_mqtt_client_domu("Diag")

        Api().add_message_callback(self.__on_message_received)
        Api().add_ready_callback(ready_callback)
        Api().start(self.mqtt_client)

    @Slot()
    def get_disks_list(self):
        Api().debug("Get disks list", "InterfaceSocle")
        Api().get_disks_list()

    @Slot(str, str)
    def get_disk_content(self, disk, from_dir=""):
        Api().get_files_list(disk, False, from_dir)
        self.folderChanged.emit(from_dir)
    
    @Slot()
    def get_repository_content(self):
        self.get_disk_content(Constantes.REPOSITORY)

    def get_disks(self):
        return self.__disks
    
    ###
    # Fonctions privées
    #
    def __on_message_received(self, topic:str, payload:dict):        
        #print("topic: {}, payload: {}".format(topic, payload))
        
        if topic == Topics.DISK_STATE:
            disk = payload.get("disk")
            if disk is None:
                Api().error("The disk value is missing")
                return
            
            state = payload.get("state")
            if state is None:
                Api().error("The state value is missing")
                return
            
            self.diskChanged.emit(disk, state == "connected")
            if state == "connected":
                self.__disks.append(disk)
                self.disksChanged.emit()
            else:
                self.__disks.remove(disk)
                self.disksChanged.emit()

        elif topic == f"{Topics.LIST_DISKS}/response":
            disks = payload.get("disks")
            if disks is None:
                Api().error("The disks value is missing")
                return

            Api().debug(f"Disks list received : {disks}")
            self.__disks.clear()
            self.__disks.extend(["__repository__"])
            self.__disks.extend(disks)
            self.disksChanged.emit()

        elif topic == f"{Topics.LIST_FILES}/response":
            disk = payload.get("disk")
            files = payload.get("files")

            if disk is None:
                Api().error("The disk argument is missing")
                return

            if files is None:
                Api().error("The files argument is missing")
                return

            Api().debug(f"Files list received, count={len(files)}")

            # Inject the disk into the values
            for file in files:
                file["disk"] = disk

            self.filesListReceived.emit(files)

    disks = Property(list, get_disks, notify=disksChanged)
    #files = Property(list, get_files, notify=filesChanged)

from PySide6.QtCore import QObject, Signal
from PySide6.QtCore import QProcess, QTimer, QDir, Property, Slot, QPoint, QCoreApplication, Qt, QEvent, QSize
from PySide6.QtGui import QMouseEvent, QCursor
from PySide6.QtWidgets import QWidget
from psec import Api, EtatDisque, Constantes, Topics, BenchmarkId, MqttClient, MqttFactory
import threading

class InterfaceSocle(QObject):
    """! Cette classe surveille le XenBus pour échanger des messages avec les autres composants du système.    
    """

    # Member variables    
    benchmark_data_ = {}
    disks_ = []
    files_ = []
    '''
    disks_ = ["NO NAME", "Transfert", "המפתח שלי"]
    files_ = [
            { "disk": "NO NAME", "type": "file", "path": "/", "name": "fichier 1", "size": 1555222 },
            { "disk": "NO NAME", "type": "file", "path": "/", "name": "fichier 2", "size": 1542 },
            { "disk": "NO NAME", "type": "folder", "path": "/", "name": "dossier 1" },
            { "disk": "NO NAME", "type": "file", "path": "/dossier 1", "name": "fichier 3", "size": 333344 },
            { "disk": "NO NAME", "type": "folder", "path": "/dossier 1", "name": "dossier 2" },
            { "disk": "NO NAME", "type": "file", "path": "/dossier 1/dossier 2", "name": "fichier 4", "size": 12 },
            { "disk": "Transfert", "type": "file", "path": "/", "name": "super fichier", "size": 827727663 },
            { "disk": "Transfert", "type": "file", "path": "/", "name": "encore un", "size": 1111222 },
            { "disk": "המפתח שלי", "type": "file", "path": "/", "name": "קובץ", "size": 26 },
            { "disk": "המפתח שלי", "type": "file", "path": "/", "name": "לא תיקיה", "size": 12344 },
            { "disk": "__repository__", "type": "file", "path": "/", "name": "super fichier", "size": 827727663 },
            { "disk": "__repository__", "type": "file", "path": "/", "name": "encore un", "size": 1111222 }
    ]    
    '''

    # Signaux
    pret = Signal()
    diskChanged = Signal(str, bool) # nom disque, connecté
    disksChanged = Signal()
    filesChanged = Signal()    
    benchmarkDataChanged = Signal()
    fileCreated = Signal(str, str, str) # filepath, disk, footprint
    error = Signal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    @Slot()
    def start(self, ready_callback):
        self.mqtt_client = MqttFactory.create_mqtt_client_domu("Diag")

        Api().add_message_callback(self.__on_message_received)
        Api().add_ready_callback(ready_callback)
        Api().start(self.mqtt_client)

    @Slot()
    def get_liste_disques(self):
        print("Get list disks")
        Api().debug("Get disks list")
        return Api().get_disks_list()

    @Slot()
    def get_contenu_disque(self, nom):
        return Api().get_files_list(nom)

    @Slot()
    def get_contenu_depot(self):
        return self.get_contenu_disque(Constantes.REPOSITORY)

    def get_disks(self):
        return self.disks_
    
    def get_files(self):
        return self.files_
    
    def get_benchmark_data(self):
        return self.benchmark_data_

    #@Slot(str, str, str)
    def download_file(self, disk:str, folder:str, name:str):
        Api().debug("Envoi d'une commande pour le téléchargement du fichier {}{}/{}".format(disk, folder, name))
        filepath = "{}/{}".format(folder, name)
        Api().copy_file_to_storage(disk, filepath)
        #Api().lit_fichier(disk, "{}/{}".format(folder, name))

    ###
    # Fonctions privées
    #
    def __update_disks_files_list(self):
        # Demande la liste des fichiers pour chaque disque
        for disk in self.disks_:
            self.get_contenu_disque(disk)

    def __on_message_received(self, topic:str, payload:dict):        
        print("topic: {}, payload: {}".format(topic, payload))
        
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
                self.disks_.append(disk)
                self.disksChanged.emit()
                self.__update_disks_files_list()
            else:
                self.disks_.remove(disk)
                self.disksChanged.emit()
                self.files_.clear()
                self.filesChanged.emit()
        elif topic == "{}/response".format(Topics.LIST_DISKS):
            disks = payload.get("disks")
            if disks is None:
                Api().error("The disks value is missing")
                return 
                        
            Api().debug("Disks list received : {}".format(disks))
            self.disks_.clear()
            self.disks_.extend(disks)            
            self.disksChanged.emit()
            self.__update_disks_files_list()            
        elif topic == "{}/response".format(Topics.LIST_FILES):
            disk = payload.get("disk")
            files = payload.get("files")

            if disk is None:
                Api().error("The disk argument is missing")
                return
            
            if files is None:
                Api().error("The files argument is missing")
                return

            Api().debug("Files list received, count={}".format(len(files)))            
            
            # Inject the disk into the values
            for file in files:
                file["disk"] = disk

            self.files_.extend(files)            
            #self.files_[disk_name] = files
            self.filesChanged.emit()
        elif topic == "{}/response".format(Topics.BENCHMARK):            
            Api().debug("Received benchmark data: {}".format(payload))

            id = payload.get("id")

            if id is None:
                Api().error("Benchmark ID is missing")
                return
            
            if id == BenchmarkId.INPUTS:
                duration = payload.get("duration")
                iterations = payload.get("iterations")
                self.benchmark_data_ = {
                    "inputs_duration": duration,
                    "inputs_iterations": iterations
                }
                self.benchmarkDataChanged.emit()
            elif id == BenchmarkId.FILES:                        
                state = payload.get("state")
                self.benchmark_data_["files_etat"] = state
                self.benchmarkDataChanged.emit()

                if state == "error":
                    Api().error("Error during files I/O benchmark")
                    # Todo: à gérer au niveau de l'interface graphique
                elif state == "termine":
                    metrics = payload.get("metrics")
                    if metrics != None and len(metrics) > 0:
                        self.__analyze_benchmark_files_metrics(metrics)
        elif topic == "{}/response".format(Topics.CREATE_FILE):
            Api().debug("File creation response: {}".format(payload))
            success = payload.get("success")
            filepath = payload.get("filepath")
            disk = payload.get("disk")
            footprint = payload.get("footprint")

            if not success:
                self.error.emit("La création du fichier {} sur le disque {} a échoué".format(filepath, disk))
                return 
        
            self.fileCreated.emit(filepath, disk, footprint)
        elif topic == Topics.DISK_STATE:
            disk = payload.get("disk")
            state = payload.get("state")

            if disk is None or state is None:
                Api().warn("The disks state notification is malformed.")
                return
            
            if state == EtatDisque.PRESENT and disk not in self.disks_:
                print("disk added:{}".format(disk))
                self.disks_.extend(disk)
                self.disksChanged.emit()
            elif state == EtatDisque.ABSENT and disk in self.disks_:
                print("disk removed:{}".format(disk))
                self.disks_.remove(disk)
                self.diskChanged.emit()


    def __analyze_benchmark_files_metrics(self, metrics=[]):
        Api().info("Analyze benchmark metrics")

        # On recoit un tableau de données comme ceci :
        '''
            {
                "step": "write_on_disk",
                "size": 10,
                "iteration": 1,
                "duration_ms": 15.341552734375
            },
            {
                "step": "write_on_disk",
                "size": 10,
                "iteration": 2,
                "duration_ms": 6.052734375
            }
            ,
            { ... }
        '''
        
        #TODO: mettre sous forme de dictionnaire
        write_usb_10k = self.__initialize_metrics()
        read_usb_10k = self.__initialize_metrics()
        copy_repository_10k = self.__initialize_metrics()
        write_usb_100k = self.__initialize_metrics()
        read_usb_100k = self.__initialize_metrics()
        copy_repository_100k = self.__initialize_metrics()
        write_usb_500k = self.__initialize_metrics()
        read_usb_500k = self.__initialize_metrics()
        copy_repository_500k = self.__initialize_metrics()
        write_usb_1m = self.__initialize_metrics()
        read_usb_1m = self.__initialize_metrics()
        copy_repository_1m = self.__initialize_metrics()
        write_usb_10m = self.__initialize_metrics()
        read_usb_10m = self.__initialize_metrics()
        copy_repository_10m = self.__initialize_metrics()
        write_usb_100m = self.__initialize_metrics()
        read_usb_100m = self.__initialize_metrics()
        copy_repository_100m = self.__initialize_metrics()

        for metric in metrics:
            if metric["step"] == "write_on_disk":  
                if metric["size"] == 10:
                    self.__handle_metrics(metric, write_usb_10k)
                if metric["size"] == 100:
                    self.__handle_metrics(metric, write_usb_100k)
                if metric["size"] == 500:
                    self.__handle_metrics(metric, write_usb_500k)
                if metric["size"] == 1*1024:
                    self.__handle_metrics(metric, write_usb_1m)
                if metric["size"] == 10*1024:
                    self.__handle_metrics(metric, write_usb_10m)
                if metric["size"] == 100*1024:
                    self.__handle_metrics(metric, write_usb_100m)
            elif metric["step"] == "read_from_disk":
                if metric["size"] == 10:
                    self.__handle_metrics(metric, read_usb_10k)
                if metric["size"] == 100:
                    self.__handle_metrics(metric, read_usb_100k)
                if metric["size"] == 500:
                    self.__handle_metrics(metric, read_usb_500k)
                if metric["size"] == 1*1024:
                    self.__handle_metrics(metric, read_usb_1m)
                if metric["size"] == 10*1024:
                    self.__handle_metrics(metric, read_usb_10m)
                if metric["size"] == 100*1024:
                    self.__handle_metrics(metric, read_usb_100m)
            elif metric["step"] == "copy_to_repository":
                if metric["size"] == 10:
                    self.__handle_metrics(metric, copy_repository_10k)
                if metric["size"] == 100:
                    self.__handle_metrics(metric, copy_repository_100k)
                if metric["size"] == 500:
                    self.__handle_metrics(metric, copy_repository_500k)
                if metric["size"] == 1*1024:
                    self.__handle_metrics(metric, copy_repository_1m)
                if metric["size"] == 10*1024:
                    self.__handle_metrics(metric, copy_repository_10m)
                if metric["size"] == 100*1024:
                    self.__handle_metrics(metric, copy_repository_100m)

        self.benchmark_data_["write_usb_10k"] = write_usb_10k
        self.benchmark_data_["read_usb_10k"] = read_usb_10k
        self.benchmark_data_["copy_repository_10k"] = copy_repository_10k
        self.benchmark_data_["write_usb_100k"] = write_usb_100k
        self.benchmark_data_["read_usb_100k"] = read_usb_100k
        self.benchmark_data_["copy_repository_100k"] = copy_repository_100k
        self.benchmark_data_["write_usb_500k"] = write_usb_500k
        self.benchmark_data_["read_usb_500k"] = read_usb_500k
        self.benchmark_data_["copy_repository_500k"] = copy_repository_500k
        self.benchmark_data_["write_usb_1m"] = write_usb_1m
        self.benchmark_data_["read_usb_1m"] = read_usb_1m
        self.benchmark_data_["copy_repository_1m"] = copy_repository_1m
        self.benchmark_data_["write_usb_10m"] = write_usb_10m
        self.benchmark_data_["read_usb_10m"] = read_usb_10m
        self.benchmark_data_["copy_repository_10m"] = copy_repository_10m
        self.benchmark_data_["write_usb_100m"] = write_usb_100m
        self.benchmark_data_["read_usb_100m"] = read_usb_100m
        self.benchmark_data_["copy_repository_100m"] = copy_repository_100m

        Api().debug(self.benchmark_data_)
        self.benchmarkDataChanged.emit()

    def __initialize_metrics(self):
        return {
            "iterations": 0,
            "min_duration": 0.0,
            "max_duration": 0.0,
            "total_duration": 0.0
        }

    def __handle_metrics(self, metrics_in, metrics_out):
        metrics_out["iterations"] += 1
        if metrics_out["min_duration"] > metrics_in["duration_ms"]:
            metrics_out["min_duration"] = metrics_in["duration_ms"]
        if metrics_out["max_duration"] < metrics_in["duration_ms"]:
            metrics_out["max_duration"] = metrics_in["duration_ms"]
        metrics_out["total_duration"] += metrics_in["duration_ms"]

    disks = Property(list, get_disks, notify=disksChanged)
    files = Property(list, get_files, notify=filesChanged)
    benchmarkData = Property(dict, get_benchmark_data, notify=benchmarkDataChanged)
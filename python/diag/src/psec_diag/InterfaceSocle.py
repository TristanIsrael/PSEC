from PySide6.QtCore import QObject, Signal, qDebug, qWarning
from PySide6.QtCore import QProcess, QTimer, QDir, Property, Slot, QPoint, QCoreApplication, Qt, QEvent, QSize
from PySide6.QtGui import QMouseEvent, QCursor
from PySide6.QtWidgets import QWidget
from panoptiscan_lib import Journal, Api, Message, TypeMessage, Notification, TypeEvenement, EtatDisque, TypeReponse, Constantes
import threading

class InterfaceSocle(QObject):
    """! Cette classe surveille le XenBus pour échanger des messages avec les autres composants du système.    
    """

    journal = Journal("InterfaceSocle")
    api = Api()

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
        self.api.set_callback_function(self.__on_message_recu)

    @Slot()
    def demarre(self):        
        try:
            self.api.demarre()
        except Exception as e:
            self.journal.error("L'API n'est pas prête")
            self.journal.error(e)
            return        

    @Slot()
    def get_liste_disques(self):
        return self.api.get_liste_disques()

    @Slot()
    def get_contenu_disque(self, nom):
        return self.api.get_liste_fichiers(nom)

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
        self.journal.debug("Envoi d'une commande pour le téléchargement du fichier {}{}/{}".format(disk, folder, name))
        filepath = "{}/{}".format(folder, name)
        self.api.copie_fichier_dans_depot(disk, filepath)
        #self.api.lit_fichier(disk, "{}/{}".format(folder, name))

    ###
    # Fonctions privées
    #
    def __on_message_recu(self, message : Message):
        self.journal.debug("Message reçu :")
        self.journal.debug(message.to_json())

        if message.type == TypeMessage.NOTIFICATION:
            self.__on_notification_recue(message)  
        elif message.type == TypeMessage.REPONSE:
            self.__on_reponse_recue(message)

    def __on_notification_recue(self, message : Message):
        self.journal.debug("C'est une notification...")
        payload = message.payload
        data = payload.get("data")

        # Filtrage des notifications
        if payload["evenement"] == TypeEvenement.DISQUE:
            self.__gere_notification_disque(data)
        else:
            self.journal.debug("Les notifications {} ne sont pas gérées.".format(payload["evenement"]))
            return        

    def __gere_notification_disque(self, data):
        nom = data.get("nom")
        etat = data.get("etat")

        if nom == None or etat == None:
            self.journal.warn("La notification n'est pas correctement formatée")
            return
        
        self.diskChanged.emit(nom, etat == EtatDisque.PRESENT)
    
    def __on_reponse_recue(self, reponse):
        self.journal.debug("C'est une réponse...")
        if reponse.commande == TypeReponse.LISTE_DISQUES:            
            liste = reponse.data
            self.journal.debug("liste des disques reçue : {}".format(liste))
            self.disks_.clear()
            self.disks_.extend(liste)
            self.disksChanged.emit()

            # Demande la liste des fichiers pour chaque disque
            for disk in liste:
                self.get_contenu_disque(disk)
        elif reponse.commande == TypeReponse.LISTE_FICHIERS:
            liste = reponse.data
            self.journal.debug("Liste des fichiers reçue : {}".format(liste))
            disk_name = liste.get("disk")
            files = liste.get("files")
            if disk_name == "" or disk_name == None:
                self.journal.error("Le nom du disque est invalide : {}".format(disk_name))
                return 
            
            # Inject the disk into the values
            for file in files:
                file["disk"] = disk_name

            self.files_.extend(files)            
            #self.files_[disk_name] = files
            self.filesChanged.emit()
        elif reponse.commande == TypeReponse.BENCHMARK_INPUTS:
            data = reponse.data
            self.journal.debug("Données benchmark reçues : {}".format(data))
            duration = data.get("duration")
            iterations = data.get("iterations")
            self.benchmark_data_ = {
                "inputs_duration": duration,
                "inputs_iterations": iterations
            }
            self.benchmarkDataChanged.emit()
        elif reponse.commande == TypeReponse.BENCHMARK_FILES:
            data = reponse.data
            self.journal.debug("Données benchmark reçues : {}".format(data))
            etat = data.get("etat")
            self.benchmark_data_["files_etat"] = etat
            self.benchmarkDataChanged.emit()

            if etat == "erreur":
                self.journal.error("Erreur pendant le benchmark des fichiers")
                # Todo: à gérer au niveau de l'interface graphique
            elif etat == "termine":
                metrics = data.get("metrics")
                if metrics != None and len(metrics) > 0:
                    self.__analyze_benchmark_files_metrics(metrics)
        elif reponse.commande == TypeReponse.FILE_CREATION:
            data = reponse.data
            self.journal.debug("Etat création fichier reçue : {}".format(data))
            success = data.get("success")
            filepath = data.get("filepath")
            disk = data.get("disk")
            footprint = data.get("footprint")

            if not success:
                self.error.emit("La création du fichier {} sur le disque {} a échoué".format(filepath, disk))
                return 
        
            self.fileCreated.emit(filepath, disk, footprint)

    def __analyze_benchmark_files_metrics(self, metrics=[]):
        self.journal.info("Analyze benchmark metrics")

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

        self.journal.debug(self.benchmark_data_)
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
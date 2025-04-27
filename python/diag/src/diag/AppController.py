from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QWidget
from InterfaceSocle import InterfaceSocle
from hashlib import md5
from psec import Api, Parametres, Cles
import os
try:
    from psec import ControleurBenchmark
except:
    print("Le contrôleur de benchmark n'est pas disponible")

class AppController(QObject):

    fenetre_app:QWidget = None
    interface_socle:InterfaceSocle

    # Signals    
    testFinished = Signal(bool, str) # success, error    
    workerThread = None
    test_step = 0
    testfile_footprint = ""

    def __init__(self, parent = QObject()):
        QObject.__init__(self, parent)


    def set_fenetre_app(self, fenetre:QWidget):
        self.fenetre_app = fenetre


    def set_interface_socle(self, interface_socle:InterfaceSocle):
        self.interface_socle = interface_socle
        self.interface_socle.fileCreated.connect(self.__on_file_created)


    @Slot(str)
    @Slot(str, str)
    def debug(self, message:str, module:str = ""):
        print(message, module)
        Api().debug(message, module)


    @Slot(str)
    @Slot(str, str)
    def info(self, message:str, module:str = ""):
        Api().info(message, module)


    @Slot(str)
    @Slot(str, str)
    def warn(self, message:str, module:str = ""):
        Api().warn(message, module)


    @Slot(str)
    @Slot(str, str)
    def error(self, message:str, module:str = ""):
        Api().error(message, module)


    @Slot()
    def start_benchmark_inputs(self):
        ControleurBenchmark().demarre_benchmark_inputs()


    @Slot()
    def start_benchmark_files(self):
        ControleurBenchmark().demarre_benchmark_fichiers()
        

    @Slot()
    def start_test(self, step=0, args = {}):
        if len(self.interface_socle.disks) == 0:
            Api().error("start_test : Il n'y a pas de disque connecté", "AppController")
            return 
        
        disk = self.interface_socle.disks[0]
        
        if step == 0:                        
            Api().info("Démarrage des tests : étape 1", "AppController")

            # 1 - Création d'un fichier sur le support USB            
            Api().info("Création d'un fichier aléatoire", "AppController")
            repository_path = Parametres().parametre(Cles.STORAGE_PATH_DOMU)
            filepath = '/test_file'.format(repository_path)                    
            contents = os.urandom(1024*1024)

            h = md5()
            h.update(contents)
            self.testfile_footprint = h.hexdigest()

            self.interface_socle.api.create_file(filepath, disk, contents)

            # Next step after the confirmation of writing
            self.test_step = 1 

        elif step == 2:
            Api().info("Démarrage de l'étape 2", "AppController")

            # Vérification de l'étape précédente
            if self.testfile_footprint != args.get("footprint"):
                error = "L'empreinte du fichier est incorrecte"
                Api().error(error, "AppController")
                self.testFinished(False, error)
                return 

            # 2 - Copie du fichier dans le dépôt
            complete_filepath = "/test_file"
            self.interface_socle.api.lit_fichier(disk, complete_filepath)

            # Next step after the confirmation of writing
            self.test_step = 2

        elif step == 3:
            Api().info("Démarrage de l'étape 3", "AppController")

            # Vérification de l'étape précédente
            if self.testfile_footprint != args.get("footprint"):
                error = "L'empreinte du fichier est incorrecte"
                Api().error(error, "AppController")
                self.testFinished(False, error)
                return 
            
            # 3 - Copie du fichier sur le support USB
            complete_filepath = "/test_file.copy"
            self.interface_socle.api.copie_fichier(disk, complete_filepath, disk)

            # Next step after the confirmation of writing
            self.test_step = 3

        elif step == 4:
            Api().info("Démarrage de l'étape 4", "AppController")

            # Vérification de l'étape précédente
            if self.testfile_footprint != args.get("footprint"):
                error = "L'empreinte du fichier est incorrecte"
                Api().error(error, "AppController")
                self.testFinished(False, error)
                return 
            
            Api().info("Les tests sont terminés et réussis", "AppController")
            self.testFinished(True, "")


    @Slot(str, str, str)
    def __on_file_created(self, filepath, disk, footprint):
        Api().info("Le fichier {} a bien été créé sur le disque {}".format(filepath, disk), "AppController")

        if self.test_step == 1:
            Api().debug("Réponse étape 1 reçue")
            self.start_test(2, { "filepath": filepath, "disk": disk, "footprint": footprint }, "AppController")
        elif self.test_step == 2:
            Api().debug("Réponse étape 2 reçue")
            self.start_test(3, { "filepath": filepath, "disk": disk, "footprint": footprint }, "AppController")
        elif self.test_step == 3:
            Api().debug("Réponse étape 3 reçue")
            self.start_test(4, { "filepath": filepath, "disk": disk, "footprint": footprint }, "AppController")
   
from PySide6.QtCore import QObject, QPoint, Signal, Slot, Property, QCoreApplication, QEvent, Qt, QThread, QTimer
from PySide6.QtGui import QCursor, QScreen, QGuiApplication
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QHoverEvent, QMouseEvent
from MousePointer import MousePointer
from InterfaceInputs import InterfaceInputs
from InterfaceSocle import InterfaceSocle
from hashlib import md5
from psec import MouseWheel, Journal, Parametres, Cles
import os
try:
    from psec import ControleurBenchmark
except:
    print("Le contrôleur de benchmark n'est pas disponible")

class AppController(QObject):

    _mouse_x = 0
    _mouse_y = 0
    _clic_x = 0
    _clic_y = 0
    _wheel = MouseWheel.NO_MOVE
    _follow_mouse_cursor = False
    fenetre_app:QWidget = None
    mousePointer:MousePointer = MousePointer()
    interfaceInputs = None
    interface_socle:InterfaceSocle

    mouseXChanged = Signal()
    mouseYChanged = Signal()
    clicXChanged = Signal()
    clicYChanged = Signal()
    wheelChanged = Signal()
    testFinished = Signal(bool, str) # success, error
    followMouseCursorChanged = Signal()
    workerThread = None
    journal = Journal("AppController")
    test_step = 0
    testfile_footprint = ""

    def __init__(self, parent = QObject()):
        QObject.__init__(self, parent)

    def __mouse_x(self):
        return self._mouse_x
    
    def set_mouse_x(self, x:int):
        self._mouse_x = x
        self.mouseXChanged.emit()
    
    def __mouse_y(self):
        return self._mouse_y
    
    def set_mouse_y(self, y:int):
        self._mouse_y = y
        self.mouseYChanged.emit()
    
    def __clic_x(self):
        return self._clic_x
    
    def set_clic_x(self, x:int):
        self._clic_x = x
        self.clicXChanged.emit()
    
    def __clic_y(self):
        return self._clic_y
    
    def set_clic_y(self, y:int):
        self._clic_y = y
        self.clicYChanged.emit()

    def __wheel(self):
        return self._wheel

    def set_wheel(self, wheel:MouseWheel):
        self._wheel = wheel
        self.wheelChanged.emit()

    def __follow_mouse_cursor(self):
        return self._follow_mouse_cursor

    def set_follow_mouse_cursor(self, follow:bool):
        self._follow_mouse_cursor = follow
        self.followMouseCursorChanged.emit()

    def set_fenetre_app(self, fenetre:QWidget):
        self.fenetre_app = fenetre
        self.mousePointer = MousePointer(fenetre.contentItem())
        self.demarre_surveillance_inputs()

    def set_interface_socle(self, interface_socle:InterfaceSocle):
        self.interface_socle = interface_socle
        self.interface_socle.fileCreated.connect(self.__on_file_created)

    @Slot()
    def start_benchmark_inputs(self):
        ControleurBenchmark().demarre_benchmark_inputs()

    @Slot()
    def start_benchmark_files(self):
        ControleurBenchmark().demarre_benchmark_fichiers()
        
    @Slot()
    def start_test(self, step=0, args = {}):
        if len(self.interface_socle.disks) == 0:
            self.journal.error("start_test : Il n'y a pas de disque connecté")
            return 
        
        disk = self.interface_socle.disks[0]
        
        if step == 0:                        
            self.journal.info("Démarrage des tests : étape 1")

            # 1 - Création d'un fichier sur le support USB            
            self.journal.info("Création d'un fichier aléatoire")
            repository_path = Parametres().parametre(Cles.CHEMIN_DEPOT_DOMU)
            filepath = '/test_file'.format(repository_path)                    
            contents = os.urandom(1024*1024)

            h = md5()
            h.update(contents)
            self.testfile_footprint = h.hexdigest()

            self.interface_socle.api.create_file(filepath, disk, contents)

            # Next step after the confirmation of writing
            self.test_step = 1 
        elif step == 2:
            self.journal.info("Démarrage de l'étape 2")

            # Vérification de l'étape précédente
            if self.testfile_footprint != args.get("footprint"):
                error = "L'empreinte du fichier est incorrecte"
                self.journal.error(error)
                self.testFinished(False, error)
                return 

            # 2 - Copie du fichier dans le dépôt
            complete_filepath = "/test_file"
            self.interface_socle.api.lit_fichier(disk, complete_filepath)

            # Next step after the confirmation of writing
            self.test_step = 2
        elif step == 3:
            self.journal.info("Démarrage de l'étape 3")            

            # Vérification de l'étape précédente
            if self.testfile_footprint != args.get("footprint"):
                error = "L'empreinte du fichier est incorrecte"
                self.journal.error(error)
                self.testFinished(False, error)
                return 
            
            # 3 - Copie du fichier sur le support USB
            complete_filepath = "/test_file.copy"
            self.interface_socle.api.copie_fichier(disk, complete_filepath, disk)

            # Next step after the confirmation of writing
            self.test_step = 3
        elif step == 4:
            self.journal.info("Démarrage de l'étape 4")

            # Vérification de l'étape précédente
            if self.testfile_footprint != args.get("footprint"):
                error = "L'empreinte du fichier est incorrecte"
                self.journal.error(error)
                self.testFinished(False, error)
                return 
            
            self.journal.info("Les tests sont terminés et réussis")
            self.testFinished(True, "")
    
    @Slot()
    def on_wheel(self, wheel:MouseWheel):
        self.set_wheel(wheel)
        
    cibleGlob = QPoint(530, 143) # en coordonnées globales    
    currentPos = QPoint(0, 0) 
    
    @Slot()
    def __do_simule_souris(self):
        #print("Démarre la simulation")

        if self.currentPos.x() < self.cibleGlob.x():
            self.currentPos.setX(self.currentPos.x()+1)
            localPos = self.fenetre_app.mapFromGlobal(self.currentPos)
            event = QMouseEvent(QEvent.MouseMove, localPos, self.currentPos, Qt.NoButton, Qt.NoButton, Qt.NoModifier)
            QCoreApplication.sendEvent(self.fenetre_app, event)            
            self._mouse_x = localPos.x()
            self._mouse_y = localPos.y()
            self.mousePointer.on_nouvelle_position(localPos)        

        if self.currentPos.y() < self.cibleGlob.y():
            self.currentPos.setY(self.currentPos.y()+1)   
            localPos = self.fenetre_app.mapFromGlobal(self.currentPos)
            event = QMouseEvent(QEvent.MouseMove, localPos, self.currentPos, Qt.NoButton, Qt.NoButton, Qt.NoModifier)
            QCoreApplication.sendEvent(self.fenetre_app, event)
            self._mouse_x = localPos.x()
            self._mouse_y = localPos.y()
            self.mousePointer.on_nouvelle_position(localPos)

        if self.currentPos.x() < self.cibleGlob.x() or self.currentPos.y() < self.cibleGlob.y():
            QTimer.singleShot(1, self.__do_simule_souris)
        else:
            print("Clic sur le composant")
            event = QMouseEvent(QEvent.MouseButtonPress, localPos, self.currentPos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
            QCoreApplication.sendEvent(self.fenetre_app, event)
            event = QMouseEvent(QEvent.MouseButtonRelease, localPos, self.currentPos, Qt.LeftButton, Qt.NoButton, Qt.NoModifier)
            QCoreApplication.sendEvent(self.fenetre_app, event)
            
            print("déplacement")
            self.currentPos.setY(self.currentPos.y()+30)   
            localPos = self.fenetre_app.mapFromGlobal(self.currentPos)
            event = QMouseEvent(QEvent.MouseMove, localPos, self.currentPos, Qt.NoButton, Qt.NoButton, Qt.NoModifier)
            QCoreApplication.sendEvent(self.fenetre_app, event)
            self._mouse_x = localPos.x()
            self._mouse_y = localPos.y()
            self.mousePointer.on_nouvelle_position(localPos)


    @Slot()
    def simule_souris(self):    
        self.workerThread = QThread()
        self.moveToThread(self.workerThread)                        
        self.workerThread.start()
        QTimer.singleShot(1, self.__do_simule_souris)

    @Slot(QPoint)
    def on_nouvelle_position(self, position:QPoint):
        self.mousePointer.on_nouvelle_position(position)

        if self.followMouseCursor:           
            self.set_mouse_x(position.x())
            self.set_mouse_y(position.y())

    @Slot(QPoint)
    def on_clicked(self, position:QPoint):
        self.set_clic_x(position.x())
        self.set_clic_y(position.y())

    @Slot() 
    def demarre_surveillance_inputs(self):
        self.journal.debug("Démarrage de la surveillance des entrées")
        self.interfaceInputs = InterfaceInputs(self.fenetre_app)  
        self.workerThread = QThread()        
        self.interfaceInputs.moveToThread(self.workerThread)  
        self.workerThread.start()
        self.interfaceInputs.nouvellePosition.connect(self.on_nouvelle_position)
        self.interfaceInputs.clicked.connect(self.on_clicked)
        self.interfaceInputs.wheel.connect(self.on_wheel)
        QTimer.singleShot(1, self.interfaceInputs.demarre_surveillance)    

    @Slot(str, str, str)
    def __on_file_created(self, filepath, disk, footprint):
        self.journal.info("Le fichier {} a bien été créé sur le disque {}".format(filepath, disk))

        if self.test_step == 1:
            self.journal.debug("Réponse étape 1 reçue")
            self.start_test(2, { "filepath": filepath, "disk": disk, "footprint": footprint })
        elif self.test_step == 2:
            self.journal.debug("Réponse étape 2 reçue")
            self.start_test(3, { "filepath": filepath, "disk": disk, "footprint": footprint })
        elif self.test_step == 3:
            self.journal.debug("Réponse étape 3 reçue")
            self.start_test(4, { "filepath": filepath, "disk": disk, "footprint": footprint })

    mouseX = Property(int, __mouse_x, notify=mouseXChanged)
    mouseY = Property(int, __mouse_y, notify=mouseYChanged)
    clicX = Property(int, __clic_x, notify=clicXChanged)
    clicY = Property(int, __clic_y, notify=clicYChanged)
    wheel = Property(int, __wheel, notify=wheelChanged)
    followMouseCursor = Property(bool, __follow_mouse_cursor, set_follow_mouse_cursor, notify=followMouseCursorChanged)
    
    
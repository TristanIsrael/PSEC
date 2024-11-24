from PySide6.QtCore import QObject, Signal, qDebug, qWarning, QTimer
from PySide6.QtCore import  Slot, QPoint, QCoreApplication, Qt, QEvent, QPointF
from PySide6.QtGui import QMouseEvent, QWheelEvent, QHoverEvent, QEnterEvent, QGuiApplication
from PySide6.QtWidgets import QWidget
from MousePointer import MousePointer
from psec import Journal, Parametres, Cles, Mouse, MouseButton, MouseWheel, MouseMove
import serial, subprocess #, threading

class InterfaceInputs(QObject):
    """! Cette classe traite les informations sur les entrées (clavier, souris et tactile) en provenance du socle.

    """

    journal = Journal("InterfaceInputs")
    fenetre_app:QWidget = None
    dernier_bouton = Qt.NoButton
    chemin_socket_inputs = None   
    socket_inputs = None 
    mouse = Mouse()

    # Signaux
    pret = Signal()
    nouvellePosition = Signal(QPoint)
    clicked = Signal(QPoint)
    wheel = Signal(MouseWheel)


    def __init__(self, fenetre_app:QWidget, parent:QObject=None):
        QObject.__init__(self, parent)
        self.fenetre_app = fenetre_app
        
    @Slot()
    def demarre_surveillance(self):        
        try:
            self.journal.info("Démarrage de la surveillance des inputs")    
            self.chemin_socket_inputs = Parametres().parametre(Cles.CHEMIN_SOCKET_INPUT_DOMU)
            self.__connecte_interface_xenbus()
        except Exception as e:
            self.journal.error("Impossible d'ouvrir le port Xenbus Inputs")
            self.journal.error(e)

    def mock(self):       
        print("MOCK") 
        for x in range(100):
            for y in range(100):
                self.nouvellePosition.emit(QPoint(x, y))        

    ###
    # Fonctions privées
    #
    def __connecte_interface_xenbus(self):
        #Ouvre le flux avec la socket
        self.journal.debug("Ouvre le flux avec le port série Inputs %s" % self.chemin_socket_inputs)

        try:
            self.socket_inputs:serial.Serial = serial.Serial(port= self.chemin_socket_inputs)
            self.journal.info("La surveillance des entrées est démarrée")     
            self.pret.emit()       
        except serial.SerialException as e:
            self.journal.error("Impossible de se connecter au port série %s" % self.chemin_socket_inputs)
            self.journal.error(e)  
            return
        
        try:
            while True:
                data = self.socket_inputs.read_until(b'\n') 

                #print("Données reçues depuis le Xenbus : {0}".format(data))
                self.__traite_donnees_input(data[:-1])

        except serial.SerialException as e:
            self.journal.error("Erreur de lecture sur le port inputs %s" % self.chemin_socket_inputs)
            self.journal.error(e)    

    def __traite_donnees_input(self, data:bytes):
        # On recoit une version sérialisée d'un objet
        # Pour l'instant on ne traite que la classe Mouse
        mouse = Mouse.fromData(data)
        if mouse != None:
            self.__traite_donnees_souris(mouse)

    def __traite_donnees_souris(self, mouse:Mouse):
        # Si c'est du tactile il faut recalculer la position en fonction de la résolution de la dalle tactile
        # Les coordonnées sont transmises en pourcentage des dimensions de la dalle
        newY:float=0.0
        newY:float=0.0

        if mouse.move == MouseMove.RELATIVE:
            newX = self.mouse.x + mouse.x
            newY = self.mouse.y + mouse.y
        elif mouse.move == MouseMove.ABSOLUTE:            
            newCoord = self.__convert_tactile_to_window(mouse)            
            newX = newCoord.x()
            newY = newCoord.y()           
            #print(mouse.x, self.fenetre_app.width(), newX, newY)        

        # On limite aux dimensions de l'écran
        self.mouse.x = max(0, min(self.fenetre_app.width(), newX))
        self.mouse.y = max(0, min(self.fenetre_app.height(), newY))
        screenPos = QPoint(self.mouse.x, self.mouse.y)
        
        # On émet le signal de la nouvelle position        
        event = QMouseEvent(QEvent.MouseMove, screenPos, screenPos, Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        QCoreApplication.postEvent(self.fenetre_app, event)
        self.nouvellePosition.emit(screenPos)
        
        # Ensuite on regarde s'il y a eu un changement sur les boutons
        if not self.mouse.buttons_equal(mouse):
            self.__genere_evt_bouton_souris(mouse, MouseButton.LEFT, screenPos)
            self.__genere_evt_bouton_souris(mouse, MouseButton.MIDDLE, screenPos)
            self.__genere_evt_bouton_souris(mouse, MouseButton.RIGHT, screenPos)
            self.mouse.buttons = mouse.buttons

            # On émet le signal du clic
            self.clicked.emit(screenPos)

        # Enfin on gère l'action sur la molette        
        if not self.mouse.wheel_equals(mouse):
            angleDelta = QPoint(0, 120 if mouse.wheel == MouseWheel.UP else -120)
            pixelDelta = QPoint(0, 2 if mouse.wheel == MouseWheel.UP else -2)
            localPos = screenPos # On est en plein écran
            
            event = QWheelEvent(localPos, screenPos, pixelDelta, angleDelta, Qt.NoButton, Qt.KeyboardModifier.NoModifier, Qt.NoScrollPhase, False)
            QCoreApplication.postEvent(self.fenetre_app, event)
            
            self.wheel.emit(mouse.wheel)
            #self.journal.debug("wheel {}".format(mouse.wheel))            

            self.mouse.wheel = MouseWheel.NO_MOVE

    def __genere_evt_bouton_souris(self, mouse:Mouse, button: int, screenPos: int):
        qbutton = Qt.LeftButton if button == MouseButton.LEFT else Qt.MiddleButton if button == MouseButton.MIDDLE else Qt.RightButton

        # Le tracking des boutons fonctionne de la façon suivante :
        # - si l'état des boutons est différent par rapport à la dernière valeur connue
        #   - alors si c'est le bouton gauche et qu'il est actif : on envoie le signal MouseButtonPress pour le bouton gauche
        #   - etc

        if not mouse.button_equals(self.mouse, button):
            if mouse.button_pressed(button): # Si le bouton est actuellement appuyé
                event = QMouseEvent(QEvent.MouseButtonPress, screenPos, screenPos, qbutton, qbutton, Qt.KeyboardModifier.NoModifier)
                QCoreApplication.postEvent(self.fenetre_app, event)
            else: # Sinon le bouton n'est plus appuyé
                # L'événement MouseButtonRelease doit être différé pour être pris en compte
                event = QMouseEvent(QEvent.MouseButtonRelease, screenPos, screenPos, qbutton, Qt.NoButton, Qt.KeyboardModifier.NoModifier)
                QCoreApplication.postEvent(self.fenetre_app, event)                

    def __genereMouseEvent(self, eventType: QEvent.Type, localPos: QPoint, screenPos: QPoint, button: Qt.MouseButton, buttons: Qt.MouseButtons):
        """Génère un événement de souris et l'insère dans l'event-loop de Qt

        :param eventType: Le type d'événement à générer
        :type eventType: QEvent.Type
        :param localPos: La position (x,y) de l'événement dans le référentiel du composant cliqué
        :type localPos: QPoint
        :param screenPos: La position (x,y) de l'événement dans le référentiel de l'écran physique
        :type screenPos: QPoint
        :param button: Le bouton de la souris concerné par l'action
        :type button: Qt.MouseButton
        :param buttons: Les boutons de la souris concernés par l'action
        :type buttons: Qt.MouseButtons
        :param cible: L'objet graphique qui va recevoir l'événement (une fenêtre d'application)
        :type cible: QObject
        """
        qDebug("Génération d'un événement {} aux coordonnées locales ({},{}) / écran ({},{})".format(eventType, localPos.x(), localPos.y(), screenPos.x(), screenPos.y()))

        # Création des événements press et release pour la souris
        event = QMouseEvent(eventType, localPos, screenPos, button, buttons, Qt.KeyboardModifier.NoModifier)
        QCoreApplication.postEvent(self.fenetre_app, event)

    def __mouse_buttons_to_qbuttons(self, mouse:Mouse) -> Qt.MouseButtons:        
        buttons = Qt.NoButton

        if mouse.button_pressed(MouseButton.LEFT):
            buttons &= Qt.LeftButton
        if mouse.button_pressed(MouseButton.MIDDLE):
            buttons &= Qt.MiddleButton
        if mouse.button_pressed(MouseButton.RIGHT):
            buttons &= Qt.RightButton

        return buttons    
    
    def __get_screen_rotation(self) -> int:
        result = subprocess.run(["/usr/bin/xenstore-read", "domid"], capture_output=True, text=True)
        domid = result.stdout.strip()
        result = subprocess.run(["/usr/bin/xenstore-read", "/local/domain/{}/screen_rotation".format(domid)], capture_output=True, text=True)
        orientation = int(result.stdout)

        return orientation
    
    def __convert_tactile_to_window(self, mouse):        
        #print(mouse.x, mouse.y)
        rotation = self.__get_screen_rotation()

        if rotation == 90:
            posX = mouse.x * self.fenetre_app.height()/100
            posY = mouse.y * self.fenetre_app.width()/100
            x_window = posY
            y_window = self.fenetre_app.height() - posX
        else:
            posX = mouse.x * self.fenetre_app.width()/100
            posY = mouse.y * self.fenetre_app.height()/100
            x_window = posX
            y_window = self.fenetre_app.height() - posY

        #print(posX, posY)
        #print(x_window, y_window)
        
        return QPointF(x_window, y_window)
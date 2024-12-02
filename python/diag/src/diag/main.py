#!/bin/python3

import os
from pathlib import Path
import sys, threading

curdir = os.path.dirname(__file__)
libdir = os.path.realpath(curdir+"/../../../lib/src") # Pour le débogage local
sys.path.append(libdir)

from PySide6.QtGui import QGuiApplication, QCursor, QMouseEvent
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType, qmlRegisterSingletonType, qmlRegisterUncreatableType, qmlRegisterSingletonInstance
from PySide6.QtCore import QObject, QCoreApplication, Qt, QEvent, QThread, QPoint, QSize
from PySide6.QtQuickControls2 import QQuickStyle
from psec import Api, ControleurBenchmark

from InterfaceSocle import InterfaceSocle
import rc_ressources
from AppController import AppController
from DiskModel import DiskModel
from DiskProxyModel import DiskProxyModel

'''
class MouseEventFilter(QObject):
    def eventFilter(self, obj, event):
        # Vérifier si l'événement est un événement de souris
        if event.type() == QMouseEvent.MouseMove:
            pos = event.position()  # Utilisation de position() pour obtenir un QPointF
            print(f"Mouse move event at ({pos.x()}, {pos.y()})")
        elif event.type() == QMouseEvent.MouseButtonPress:
            pos = event.position()
            print(f"Mouse button pressed at ({pos.x()}, {pos.y()})")
        elif event.type() == QMouseEvent.MouseButtonRelease:
            pos = event.position()
            print(f"Mouse button released at ({pos.x()}, {pos.y()})")
        elif event.type() == QMouseEvent.Wheel:
            pos = event.position()
            print(f"Mouse wheel event at ({pos.x()}, {pos.y()}, {event.angleDelta()})")

        # Passer l'événement à la gestion normale
        return super().eventFilter(obj, event)
'''

api_ready = threading.Event()

def on_ready():
    print("PSEC API is ready")
    api_ready.set()
    ControleurBenchmark().setup(Api().get_mqtt_client())

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    QQuickStyle.setStyle("Universal")

    appController = AppController()
    interfaceSocle = InterfaceSocle(app)
    interfaceSocle.start(on_ready)

    print("Waiting for the API to be ready")
    api_ready.wait()
    
    diskModel = DiskModel(interfaceSocle, app)

    # Expose les Types QML
    qmlRegisterSingletonInstance(AppController, "net.alefbet", 1, 0, 'AppController', appController)
    qmlRegisterSingletonInstance(InterfaceSocle, "net.alefbet", 1, 0, 'InterfaceSocle', interfaceSocle)
    qmlRegisterSingletonInstance(DiskModel, "net.alefbet", 1, 0, 'DiskModel', diskModel)
    qmlRegisterType(DiskProxyModel, "net.alefbet", 1, 0, 'DiskProxyModel')

    app_root_path = Path(__file__).parent
    engine = QQmlApplicationEngine()    
    qml_file = app_root_path / 'qml/main.qml'
    engine.load(qml_file.as_uri())

    if not engine.rootObjects():
        sys.exit(-1)

    qml_root = engine.rootObjects()[0]        
    qml_root.showFullScreen()

    # Intégration avec le socle
    appController.set_fenetre_app(qml_root)    
    appController.set_interface_socle(interfaceSocle)    

    #mouseEventFilter = MouseEventFilter()
    #qml_root.installEventFilter(mouseEventFilter)

    Api().info("Application started")

    app.exec()
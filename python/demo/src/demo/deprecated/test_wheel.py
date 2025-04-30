
import os, sys, threading, time
from pathlib import Path

curdir = os.path.dirname(__file__)
libdir = os.path.realpath(curdir+"/../../../lib/src") # Pour le débogage local
sys.path.append(libdir)

from PySide6.QtCore import QObject, QEvent, QPoint, Qt, QCoreApplication, QTimer
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType, qmlRegisterSingletonInstance
from PySide6.QtWidgets import QApplication, QMainWindow, QComboBox
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtGui import QHoverEvent, QMouseEvent
from InterfaceSocle import InterfaceSocle
from python.diag.src.diag.deprecated.InterfaceInputs import InterfaceInputs
import rc_ressources
from AppController import AppController
from python.diag.src.diag.deprecated.MousePointer import MousePointer
from DiskModel import DiskModel
from python.diag.src.diag.deprecated.DiskProxyModel import DiskProxyModel
from python.diag.src.diag.deprecated.MousePointer import MousePointer

class EvtFilter(QObject):
    def eventFilter(self, obj, event):              
        if event.type() == QEvent.HoverEnter or event.type() == QEvent.HoverMove:
            print(event, event.oldPos())
        elif event.type() == QEvent.MouseButtonPress or event.type() == QEvent.MouseButtonRelease:
            print(event, event.button(), event.buttons())
        elif event.type() == QEvent.MouseMove:
            print(event, event.button(), event.buttons())
        else:
            print(event)

        return False
        #return QMainWindow.eventFilter(obj, event)
        #print("position:", event.position())
        #print("globalPositionl:", event.globalPosition())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QQuickStyle.setStyle("Universal")
    appController = AppController(app)

    qmlRegisterSingletonInstance(AppController, "net.alefbet", 1, 0, 'AppController', appController)
    #qmlRegisterSingletonInstance(InterfaceSocle, "net.alefbet", 1, 0, 'InterfaceSocle', interfaceSocle)
    #qmlRegisterSingletonInstance(DiskModel, "net.alefbet", 1, 0, 'DiskModel', diskModel)
    qmlRegisterType(DiskProxyModel, "net.alefbet", 1, 0, 'DiskProxyModel')

    app_root_path = Path(__file__).parent
    engine = QQmlApplicationEngine()    
    qml_file = app_root_path / 'qml/main.qml'
    engine.load(qml_file.as_uri())

    if not engine.rootObjects():
        sys.exit(-1)

    qml_root = engine.rootObjects()[0] 
    qml_root.setX(0)
    qml_root.setY(0)
    appController.set_fenetre_app(qml_root)
    mousePointer = MousePointer(qml_root.contentItem())
    appController.mousePointer = mousePointer

    #qml_root.installEventFilter(EvtFilter(app))    
    app.exec()
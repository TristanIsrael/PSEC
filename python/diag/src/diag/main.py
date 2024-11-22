#!/bin/python3

import os
from pathlib import Path
import sys

curdir = os.path.dirname(__file__)
libdir = os.path.realpath(curdir+"/../../../lib/src") # Pour le débogage local
sys.path.append(libdir)

from PySide6.QtGui import QGuiApplication, QCursor
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType, qmlRegisterSingletonType, qmlRegisterUncreatableType, qmlRegisterSingletonInstance
from PySide6.QtCore import QObject, QCoreApplication, Qt, qInstallMessageHandler, QEvent, QThread, qWarning, QPoint, QSize
from PySide6.QtQuickControls2 import QQuickStyle

from InterfaceSocle import InterfaceSocle
from InterfaceInputs import InterfaceInputs
import rc_ressources
from AppController import AppController
from MousePointer import MousePointer
from DiskModel import DiskModel
from DiskProxyModel import DiskProxyModel

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

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    QQuickStyle.setStyle("Universal")

    appController = AppController()
    interfaceSocle = InterfaceSocle(app)
    interfaceSocle.demarre()
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
 
    app.exec()
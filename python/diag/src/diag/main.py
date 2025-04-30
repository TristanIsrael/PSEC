#!/bin/python3

import os
from pathlib import Path
import sys, threading

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType, qmlRegisterSingletonType, qmlRegisterUncreatableType, qmlRegisterSingletonInstance
from psec import Api, System
from AppController import AppController

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)

    # Expose les Types QML
    qmlRegisterSingletonInstance(AppController, "net.alefbet", 1, 0, 'AppController', AppController(app))

    app_root_path = Path(__file__).parent
    engine = QQmlApplicationEngine()
    engine.addImportPath(app_root_path / 'qml')
    qml_file = app_root_path / 'qml/main.qml'
    engine.load(qml_file.as_uri())

    if not engine.rootObjects():
        sys.exit(-1)

    qml_root = engine.rootObjects()[0]
    if os.getenv("DEVMODE") is None:
        qml_root.showFullScreen()

    app.exec()
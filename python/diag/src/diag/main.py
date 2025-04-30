#!/bin/python3

import os
import signal
from pathlib import Path
import sys, threading

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType, qmlRegisterSingletonType, qmlRegisterUncreatableType, qmlRegisterSingletonInstance
from AppController import AppController

app = QGuiApplication(sys.argv)

def handle_sigint(signum, frame):    
    app.quit()  # Quitte la boucle Qt

signal.signal(signal.SIGINT, handle_sigint)

if __name__ == '__main__':
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
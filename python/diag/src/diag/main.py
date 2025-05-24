#!/bin/python3

import os
import signal
from pathlib import Path
import sys, threading

from PySide6.QtCore import QUrl, Qt, QTimer
from PySide6.QtGui import QKeyEvent, QKeySequence, QGuiApplication, QFont
from PySide6.QtQuick import QQuickView
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType, qmlRegisterSingletonType, qmlRegisterUncreatableType, qmlRegisterSingletonInstance
from AppController import AppController

class MyView(QQuickView):
    def keyPressEvent(self, event: QKeyEvent):
        # Vérifie si Ctrl+C est pressé
        print(event.modifiers(), Qt.ControlModifier, event.key())
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C:            
            self.close()
            QGuiApplication.quit()
        else:
            super().keyPressEvent(event)

def main():
    app = QGuiApplication(sys.argv)

    signal.signal(signal.SIGINT, lambda *_: app.quit())
    
    # Expose les Types QML
    qmlRegisterSingletonInstance(AppController, "net.alefbet", 1, 0, 'AppController', AppController(app))

    # Install font
    font = QFont("Roboto", 18)
    app.setFont(font)

    app_root_path = Path(__file__).parent
    #engine = QQmlApplicationEngine()
    view = MyView()

    view.engine().quit.connect(app.quit)
    view.engine().addImportPath(app_root_path / 'qml')
    #engine.addImportPath(app_root_path / 'qml')
    qml_file = app_root_path / 'qml/main.qml'
    view.setSource(qml_file.as_uri())
    #engine.load(qml_file.as_uri())
    if os.getenv("DEVMODE") is None:
        view.showFullScreen()

    #if not engine.rootObjects():
    #    sys.exit(-1)

    #qml_root = engine.rootObjects()[0]
    #if os.getenv("DEVMODE") is None:
    #    qml_root.showFullScreen()

    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
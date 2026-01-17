#!/bin/python3

import os
import signal
import pkgutil
from pathlib import Path
import sys

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QKeyEvent, QGuiApplication, QFont
from PySide6.QtQuick import QQuickView
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType, qmlRegisterSingletonType, qmlRegisterUncreatableType, qmlRegisterSingletonInstance
from app_controller import AppController

class MyView(QQuickView):
    def keyPressEvent(self, event: QKeyEvent):
        # print(event.modifiers(), Qt.ControlModifier, event.key())
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C:
            # Ctrl+C has been pressed
            self.close()
            QGuiApplication.quit()
        else:
            super().keyPressEvent(event)

def main():
    app = QGuiApplication(sys.argv)

    signal.signal(signal.SIGINT, lambda *_: app.quit())
    
    # Expose QML Types
    qmlRegisterSingletonInstance(AppController, "PSEC", 1, 0, 'AppController', AppController(app))

    # Install font
    #font = QFont("Roboto", 18)
    #app.setFont(font)
            
    app_root_path = Path(__file__).parent
    view = MyView()
    
    view.engine().quit.connect(app.quit)
    view.engine().addImportPath(app_root_path / 'qml')
    qml_file = app_root_path / 'qml/content/MainScreen.qml'
    view.setSource(qml_file.as_uri())
    if os.getenv("DEVMODE") is None:
        view.showFullScreen()
    else:
        view.show()

    return app.exec()

if __name__ == '__main__':
    sys.exit(main())

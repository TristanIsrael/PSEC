from enum import Enum
from PySide6.QtCore import QEnum, QObject, Qt
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "PSEC"
QML_IMPORT_MAJOR_VERSION = 1

class MessageLevel(Enum):
    Information, Warning, Error = range(3)

class Roles():    
    RoleProgress = Qt.UserRole +1    
    RoleIsPackage = Qt.UserRole +2
    RoleSection = Qt.UserRole +3
    RoleLabel = Qt.UserRole +4
    RoleSuccess = Qt.UserRole +5

@QmlElement
class Enums(QObject):
    QEnum(MessageLevel)
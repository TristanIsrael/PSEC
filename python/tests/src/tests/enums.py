from enum import Enum
from PySide6.QtCore import QEnum, QObject
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "PSEC"
QML_IMPORT_MAJOR_VERSION = 1

class MessageLevel(Enum):
    Information, Warning, Error = range(3)

class Roles(Enum):
    RoleProgress, RolePackage, RoleTest = range(3)

@QmlElement
class Enums(QObject):
    QEnum(MessageLevel)
    QEnum(Roles)
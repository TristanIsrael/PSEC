from PySide6.QtCore import QObject, QAbstractListModel, QModelIndex, Qt
from InterfaceSocle import InterfaceSocle
import humanize


class DiskModel(QAbstractListModel):
    """ La classe DiskModel fournit aux vues de l'application les informations concernant les disques 
    connectés au système ainsi que les fichiers qu'ils contiennent """

    __files_list = []

    # Constantes
    RoleDisk = Qt.UserRole + 1
    RolePath = Qt.UserRole + 2
    RoleFileType = Qt.UserRole + 3
    RoleFileName = Qt.UserRole + 4
    RoleFileSize = Qt.UserRole + 5

    # Signaux
    def __init__(self, interface_socle:InterfaceSocle, parent=None):
        super().__init__(parent)

        self.__interface_socle = interface_socle
        self.__current_folder = ""

        ## Connect signals
        self.__interface_socle.disksChanged.connect(self.__on_disks_changed)
        self.__interface_socle.folderChanged.connect(self.__on_folder_changed)
        self.__interface_socle.filesListReceived.connect(self.__on_files_list_received)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        # We add a fake folder to go up
        if index.row() == 0 and self.__current_folder != "":
            return self.__data_folder_up(role)

        row = index.row()-1
        file = self.__files_list[row]

        if role == self.RoleDisk:
            return file.get("disk")
        elif role == self.RolePath:
            return file.get("path")
        elif role == self.RoleFileType:
            return file.get("type")
        elif role == self.RoleFileName:
            return file.get("name")
        elif role == self.RoleFileSize:
            return file.get("size")
        
        return "unknown"

    def rowCount(self, parent=QModelIndex()):
        length = len(self.__files_list)

        if self.__current_folder != "":
            length += 1 # Up

        return length

    def roleNames(self):
        return {
            self.RoleDisk: b'disk',
            self.RolePath: b'path',
            self.RoleFileType: b'fileType',
            self.RoleFileName: b'fileName',
            self.RoleFileSize: b'fileSize'
        }
    
    def __data_folder_up(self, role:int):
        if role == self.RoleDisk:
            return "any"
        elif role == self.RolePath:
            return QObject.tr("up")
        elif role == self.RoleFileType:
            return "special_up"
        elif role == self.RoleFileName:
            return QObject.tr("up")
        elif role == self.RoleFileSize:
            return 0
        
        return None

    def __on_disks_changed(self):
        self.beginResetModel()
        self.endResetModel()

    def __on_files_list_received(self, files_list:list):
        self.beginResetModel()
        self.__files_list = files_list
        self.endResetModel()

    def __on_folder_changed(self, folder:str):
        self.__current_folder = folder
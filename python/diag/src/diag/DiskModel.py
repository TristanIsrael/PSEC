from PySide6.QtCore import QObject, QAbstractListModel, QModelIndex, Qt
from InterfaceSocle import InterfaceSocle
import humanize


class DiskModel(QAbstractListModel):
    """ La classe DiskModel fournit aux vues de l'application les informations concernant les disques 
    connectés au système ainsi que les fichiers qu'ils contiennent """

    # Constantes
    RoleDisk = Qt.UserRole + 1
    RolePath = Qt.UserRole + 2
    RoleFileType = Qt.UserRole + 3
    RoleFileName = Qt.UserRole + 4
    RoleFileSize = Qt.UserRole + 5

    # Signaux


    # Variables membres
    interfaceSocle:InterfaceSocle = InterfaceSocle()

    # Caches locaux

    def __init__(self, interfaceSocle:InterfaceSocle, parent=None):
        super().__init__(parent)

        self.interfaceSocle = interfaceSocle

        ## Connect signals
        self.interfaceSocle.disksChanged.connect(self.__onDataChanged)
        self.interfaceSocle.filesChanged.connect(self.__onDataChanged)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        # We add a fake folder to go up
        if index.row() == 0:
            return self.__data_folder_up(role)

        row = index.row()-1
        files = self.__all_files()
        # TODO: vérifier la taille de la liste
        file = files[row]        

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
        
        return "inconnu"

    def rowCount(self, parent=QModelIndex()):        
        length = len(self.__all_files())
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

    def __all_files(self):
        return self.interfaceSocle.get_files()
        '''
        for key, value in fDict.items():
            # Inject the disk into the values
            for file in value:
                file["disk"] = key
            files.extend(value)

        return files
        '''
    
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
    
    def __onDataChanged(self):
        print("Données modifiées")
        self.beginResetModel()
        self.endResetModel()

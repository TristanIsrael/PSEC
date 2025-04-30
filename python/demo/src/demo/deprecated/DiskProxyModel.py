from PySide6.QtCore import QObject, QSortFilterProxyModel, QAbstractItemModel, QModelIndex, Property, Qt, Signal, Slot
from DiskModel import DiskModel

class DiskProxyModel(QSortFilterProxyModel):

    disk_name_:str = ""
    folder_:str = "/"

    diskNameChanged = Signal()
    folderChanged = Signal()

    def __init__(self, parent:QObject = None):
        super().__init__(parent)    
        self.sort(0)    

    ###
    # Getters and setters
    #
    def _sourceModel(self):
        return self.sourceModel()
    
    def _setSourceModel(self, source:QAbstractItemModel):
        self.setSourceModel(source)  

    def _disk_name(self):
        return self.disk_name_
    
    def _set_disk_name(self, disk_name:str):
        self.disk_name_ = disk_name
        self.diskNameChanged.emit()
        self.invalidateFilter()

    def _folder(self):
        return self.folder_

    def _set_folder(self, folder:str):
        self.folder_ += "{}{}".format("/" if self.folder_ != "/" else "", folder)
        self.folderChanged.emit()
        self.invalidateFilter()

    ###
    # Reimplemented proxy functions
    #
    def filterAcceptsRow(self, sourceRow:int, parent:QModelIndex = None):
        # Special case:
        # If the current folder is not the root fo the disk we show a special
        # "up" folder
        if self.folder_ != "/" and sourceRow == 0:
            return True

        index = self.sourceModel().index(sourceRow, 0, QModelIndex())

        disk = self.sourceModel().data(index, DiskModel.RoleDisk)
        folder = self.sourceModel().data(index, DiskModel.RolePath)
        #filename = self._sourceModel().data(index, DiskModel.RoleFileName)

        #print("index: {}, disk: {}, folder: {}, filter: {}{}".format(index, disk, folder, self.disk_name_, self.folder_))

        if self.disk_name_ != "":
            if self.disk_name_ != disk:
                return False
        
        if self.folder_ != "":
            if self.folder_ != folder:
                return False        

        return True

    def lessThan(self, source_left:QModelIndex, source_right:QModelIndex):
        indexLeft = self.sourceModel().index(source_left.row(), 0, QModelIndex())
        nameLeft = self.sourceModel().data(indexLeft, DiskModel.RoleFileName)

        indexRight = self.sourceModel().index(source_right.row(), 0, QModelIndex())
        nameRight = self.sourceModel().data(indexRight, DiskModel.RoleFileName)

        #print("{} < {} : {}".format(nameLeft, nameRight, nameLeft < nameRight))  

        if nameLeft == "up":
            return True 
        elif nameRight == "up":
            return False      

        return nameLeft < nameRight

    ### 
    # Slots
    #
    @Slot()
    def go_up(self):
        if self.folder_ != "" and self.folder_ != "/":
            fld = self.folder_.split("/")
            new_folder = "/".join(fld[:-1])
            self.folder_ = new_folder if new_folder != "" else "/"
            self.invalidateFilter()

    ### 
    # Properties
    #
    source = Property(QObject, _sourceModel, _setSourceModel)
    disk = Property(str, _disk_name, _set_disk_name, notify= diskNameChanged)
    folder = Property(str, _folder, _set_folder, notify= folderChanged)
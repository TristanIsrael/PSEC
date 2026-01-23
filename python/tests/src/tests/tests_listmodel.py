from PySide6.QtCore import QObject, QAbstractListModel, QModelIndex, Signal
from enums import Roles, MessageLevel
from tests_helper import TestsHelper

class TestsListModel(QAbstractListModel):

    __cache = [] # List of dicts

    addMessage = Signal(str, MessageLevel)

    def __init__(self, parent:QObject):
        super().__init__(parent)        

    def update_cache(self):
        """ The cache contains all tests automatically discovered """
        self.__cache = TestsHelper.get_tests_list()
        

    def rowCount(self, parent=QModelIndex()):
        #return len(self.__cache.keys()) + len(self.__cache.values())
        return len(self.__cache)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        
        if len(self.__cache) <= index.row():
            return

        item = self.__cache[index.row()]

        if role == Roles.RoleLabel:
            return item.get("name")
        elif role == Roles.RoleSection:
            return not item.get("is_test")
        elif role == Roles.RoleProgress:
            if item.get("is_test"):
                return item.get("progress")
            else:
                return self.__calculate_package_progress(item.get("name"))
        elif role == Roles.RoleSuccess:
            return item.get("success")
        elif role == Roles.RoleIsPackage:
            return not item.get("is_test")
        
    def __calculate_package_progress(self, package_name) -> int:
        """ Calculates the progress for a package by calculating the mean of 
            the values for the package's tests 
        """

        tests = [d for d in self.__cache if d.get("package") == package_name]
        sum_ = sum(d.get("progress") for d in tests)
        cnt_ = len(tests)

        progress = float(sum_) / float(cnt_)if cnt_ > 0 else 0

        return progress
        

    def get_nb_capacities_total(self) -> int:
        return sum(1 for d in self.__cache if d.get("is_test") is False)
    
    def get_nb_tests_total(self) -> int:
        return sum(1 for d in self.__cache if d.get("is_test"))

    def roleNames(self) -> dict:
        roles = {
            Roles.RoleProgress: b'progress',
            Roles.RoleIsPackage: b'isPackage', 
            Roles.RoleLabel: b'label',
            Roles.RoleSuccess: b'success'
        }

        return roles

    def on_progress_changed(self):
        # TODO: improve the algorithm
        self.beginResetModel()
        self.endResetModel()
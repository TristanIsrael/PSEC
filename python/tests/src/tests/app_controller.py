from Singleton import SingletonMeta
from PySide6.QtCore import QObject, Property, Slot
from tests_listmodel import TestsListModel

class AppController(QObject):    

    def __init__(self, parent:QObject):
        super().__init__(parent)

        self.__tests_listmodel = TestsListModel(self)

    def start(self):
        pass
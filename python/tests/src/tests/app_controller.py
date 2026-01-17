from PySide6.QtCore import QObject, Property, Slot, Signal
from tests_listmodel import TestsListModel

class AppController(QObject):

    def __init__(self, parent:QObject):
        super().__init__(parent)

        self.__tests_listmodel = TestsListModel(self)

    def start(self):
        pass


    ###############
    ### Signals
    ###
    nbCapacitiesTotalChanged = Signal()
    nbTestsTotalChanged = Signal()

    ###############
    ### Properties
    ###
    @Property(QObject, constant= True)
    def testsListModel(self) -> QObject:
        return self.__tests_listmodel

    @Property(int, notify= nbCapacitiesTotalChanged)
    def nbCapacitiesTotal(self) -> int:
        return self.__tests_listmodel.get_nb_capacities_total()
    
    @Property(int, notify= nbTestsTotalChanged)
    def nbTestsTotal(self) -> int:
        return self.__tests_listmodel.get_nb_tests_total()

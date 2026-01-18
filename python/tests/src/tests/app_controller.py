from PySide6.QtCore import QObject, Property, Slot, Signal
from tests_listmodel import TestsListModel
from messages_listmodel import MessagesListModel
from enums import MessageLevel

class AppController(QObject):

    __started = False

    def __init__(self, parent:QObject):
        super().__init__(parent)
        
        self.__messages_model = MessagesListModel(self)
        self.__tests_listmodel = TestsListModel(self)
        self.__tests_listmodel.addMessage.connect(self.__messages_model.add_message)
        self.__tests_listmodel.update_cache()

        self.__messages_model.add_message(self.tr("PSEC tests app has started"))
        self.__messages_model.add_message(self.tr("Waiting for user action..."), MessageLevel.User)

    @Slot()
    def start_stop(self):
        if not self.__started:
            self.__messages_model.add_message(self.tr("Start the whole test plan"))

            self.__started = True
        else:
            self.__messages_model.add_message(self.tr("Stop the whole test plan"))


    ###############
    ### Signals
    ###
    nbCapacitiesTotalChanged = Signal()
    nbTestsTotalChanged = Signal()
    startedChanged = Signal()

    ###############
    ### Properties
    ###
    @Property(QObject, constant= True)
    def testsListModel(self) -> QObject:
        return self.__tests_listmodel

    @Property(QObject, constant= True)
    def messagesModel(self) -> QObject:
        return self.__messages_model

    @Property(int, notify= nbCapacitiesTotalChanged)
    def nbCapacitiesTotal(self) -> int:
        return self.__tests_listmodel.get_nb_capacities_total()
    
    @Property(int, notify= nbTestsTotalChanged)
    def nbTestsTotal(self) -> int:
        return self.__tests_listmodel.get_nb_tests_total()

    @Property(bool, notify= startedChanged)
    def started(self) -> bool:
        return self.__started
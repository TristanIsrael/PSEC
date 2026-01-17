from PySide6.QtCore import QObject, Signal
from enums import MessageLevel

class Message():
    """ Encapsulates a string and a level for a message sent by a test """

    message = ""
    level = MessageLevel.Information

    def __init__(self, message:str, level:MessageLevel):
        self.message = message
        self.level = level

class AbstractTest(QObject):
    """ Abstract class for developping tests """

    #### Public properties ####
    name = "A test"
    description = "Description of the test"
    parallelizable = True
    progress = 0 # From 0 to 100
    messages = []

    #### Private properties ####
    

    #################
    #### Methods ####
    #################
 
    def start(self) -> None:
        """ Called when the test is started """
        raise NotImplementedError

    def stop(self) -> None:
        """ Called when the test must be stopped """
        raise NotImplementedError

    def is_success(self) -> bool:
        """ Called to know the test result """
        raise NotImplementedError

    def _send_message(self, message:str, level:MessageLevel):
        self.messages.append(Message(message, level))
        self.message.emit(message, level)

    def _set_progress(self, progress:int):
        self.progress = progress
        self.progressChanged.emit()

    #################
    #### Signals ####
    #################
    progressChanged = Signal()
    started = Signal()
    stopped = Signal()
    finished = Signal()
    waiting = Signal()
    message = Signal(str, MessageLevel)

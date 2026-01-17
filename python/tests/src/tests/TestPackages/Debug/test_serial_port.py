from lib import AbstractTest

class TestSerialPort(AbstractTest):

    name = "Serial port"
    description = ""
    parallelizable = True

    def start(self) -> None:
        """ Called when the test is started """
        self._set_progress(100)

    def stop(self) -> None:
        """ Called when the test must be stopped """
        pass

    def is_success(self) -> bool:
        """ Called to know the test result """
        pass
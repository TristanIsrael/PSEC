from lib import AbstractTest

class TestSystemComponents(AbstractTest):

    name = "System components"
    description = "This test verifies whether the system components are correctly sent by the API"
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
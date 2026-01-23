from lib import AbstractTest
from enums import MessageLevel
from psec import Api, Topics, ApiHelper

class TestGetStoragesList(AbstractTest):

    name = "Get storages list"
    description = ""
    parallelizable = True
    __disk = {}
    __step = 0

    def start(self) -> None:
        """ Called when the test is started """
        self._set_progress(0)
 
        Api().add_message_callback(self.__on_message)
        Api().subscribe(Topics.DISK_STATE)
        
        # Ask the user to connect one storage
        self._send_message(self.tr("Please connect a storage now."), MessageLevel.User)
        self._send_message(self.tr("Waiting for a storage..."), MessageLevel.Information)
        self._set_waiting(True)
        self.__step = 1

    def stop(self) -> None:
        """ Called when the test must be stopped """
        pass

    def is_success(self) -> bool:
        """ Called to know the test result """
        pass

    def __on_message(self, topic:str, payload:dict):
        if topic == Topics.DISK_STATE:
            self.__disk["name"] = payload.get("disk")
            self.__disk["state"] = payload.get("state")

        if self.__step == 1:
            self.__step2()

    def __step2(self):
        # Verify the storage data
        if len(self.__disk) == {}:
            self._send_message(self.tr("Error: received a disk state notification but the disks list is empty"))            
            self._set_finished(False)
            return
        elif self.__disk.get("name") == "":
            self._send_message(self.tr("Error: received an empty disk name"))            
            self._set_finished(False)
            return
        else:                                
            if self.__disk.get("state") != "connected":
                self._send_message(self.tr("Error: the disk state is incorrect"))
                self._set_finished(False)
                return 
            
            # Use the API
            disk_name = ApiHelper.get_disk_name(self.__disk)
            disk_state = ApiHelper.get_disk_state(self.__disk)
            disk_connected = ApiHelper.is_disk_connected(self.__disk)

            if disk_name == "" or disk_state != "connected" or not disk_connected:
                self._send_message(self.tr("Error: the disk information return by ApiHelper is incorrect"))
                self._set_finished(False)
                return
            
        # The test is successful
        self._set_finished(True)
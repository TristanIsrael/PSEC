from psec import MockSysUsbController
from DevModeHelper import DevModeHelper
import threading

if __name__ == "__main__":
    print("Démarrage des mocks...")

    print("... Starting Mock sys-usb controller")
    mock = MockSysUsbController()
    mock.start(DevModeHelper.get_mocked_source_disk_path(), DevModeHelper.get_storage_path(), DevModeHelper.get_mocked_destination_disk_path())
    
    print("Démarrage des mocks terminé")

    lock = threading.Event()
    lock.wait()    
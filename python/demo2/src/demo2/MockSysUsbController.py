from psec import MockSysUsbController
import threading

SOURCE_DISK = "/Applications" # Modifier avec C:\ par exemple sous Windows
STORAGE_PATH = "/tmp"
DESTINATION_DISK = ""

if __name__ == "__main__":
    print("... Starting Mock sys-usb controller")
    mockUSB = MockSysUsbController()
    mockUSB.start(SOURCE_DISK, STORAGE_PATH, DESTINATION_DISK)    
    threading.Event().wait()
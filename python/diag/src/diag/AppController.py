import cpuinfo
import subprocess
import os
import psutil
from Singleton import SingletonMeta
from PySide6.QtCore import QObject, Property, Slot

class AppController(QObject):

    def __get_system_info(self) -> dict:        
        cpu = cpuinfo.get_cpu_info()
        return cpu
    
    def has_vtd(self):        
        ''' AKA VT-d '''
        cmd = "dmesg | grep -i -e iommu -e dmar"

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)

            if result.returncode == 0 and "DMAR: Intel(R) Virtualization Technology for Directed I/O" in result.stdout:
                return True
        except subprocess.CalledProcessError:
            return False
        
        return False
        
    def has_ept(self):
        cmd = "xl dmesg | grep -i ept"

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)

            if result.returncode == 0 and "(XEN) Intel VT-d Shared EPT tables enabled" in result.stdout:
                return True
        except subprocess.CalledProcessError:
            return False
        
        return False
    
    def has_hvm(self):
        return os.path.exists("/dev/kvm")
    
    def get_installed_memory_in_gb(self):
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024 ** 3)
        return total_gb
    
    @Slot()
    def shutdown(self):
        subprocess.run("shutdown", check=False)

    cpuInfo = Property(type=dict, fget=__get_system_info, constant=True)
    hasVTd = Property(type=bool, fget=has_vtd, constant=True)
    hasHVM = Property(type=bool, fget=has_hvm, constant=True)
    installedMemory = Property(type=float, fget=get_installed_memory_in_gb, constant=True)
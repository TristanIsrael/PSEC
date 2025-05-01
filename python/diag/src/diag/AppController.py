import cpuinfo
import subprocess
import os
import psutil
from Singleton import SingletonMeta
from PySide6.QtCore import QObject, Property, Slot

class AppController(QObject):

    def __get_system_info(self) -> dict:
        '''
        {
            "python_version": "3.12.9.final.0 (64 bit)",
            "cpuinfo_version": [
                9,
                0,
                0
            ],
            "cpuinfo_version_string": "9.0.0",
            "arch": "X86_64",
            "bits": 64,
            "count": 12,
            "arch_string_raw": "x86_64",
            "vendor_id_raw": "GenuineIntel",
            "brand_raw": "12th Gen Intel(R) Core(TM) i5-1230U",
            "hz_advertised_friendly": "1.6896 GHz",
            "hz_actual_friendly": "1.6896 GHz",
            "hz_advertised": [
                1689603000,
                0
            ],
            "hz_actual": [
                1689603000,
                0
            ],
            "stepping": 4,
            "model": 154,
            "family": 6,
            "flags": [
                "3dnowprefetch",
                "abm",
                "acpi",
                "adx",
                "aes",
                "apic",
                "arch_capabilities",
                "avx",
                "avx2",
                "avx_vnni",
                "bmi1",
                "bmi2",
                "clflush",
                "clflushopt",
                "clwb",
                "cmov",
                "constant_tsc",
                "cpuid",
                "cpuid_fault",
                "cx16",
                "cx8",
                "de",
                "erms",
                "est",
                "f16c",
                "fma",
                "fpu",
                "fsgsbase",
                "fsrm",
                "fxsr",
                "gfni",
                "ht",
                "hypervisor",
                "ibpb",
                "ibrs",
                "ibrs_enhanced",
                "lahf_lm",
                "lm",
                "mca",
                "mce",
                "md_clear",
                "mmx",
                "monitor",
                "movbe",
                "msr",
                "nonstop_tsc",
                "nopl",
                "nx",
                "osxsave",
                "pae",
                "pat",
                "pclmulqdq",
                "pni",
                "popcnt",
                "rdpid",
                "rdrand",
                "rdrnd",
                "rdseed",
                "rdtscp",
                "rep_good",
                "sep",
                "serialize",
                "sha",
                "sha_ni",
                "ss",
                "ssbd",
                "sse",
                "sse2",
                "sse4_1",
                "sse4_2",
                "ssse3",
                "stibp",
                "syscall",
                "tsc",
                "tsc_known_freq",
                "vaes",
                "vpclmulqdq",
                "xgetbv1",
                "xsave",
                "xsavec",
                "xsaveopt"
            ],
            "l3_cache_size": 12582912,
            "l2_cache_size": 65536,
            "l2_cache_line_size": 1280,
            "l2_cache_associativity": 7
        }
        '''

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
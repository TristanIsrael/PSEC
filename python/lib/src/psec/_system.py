import subprocess
import platform
import os
import json
from . import SingletonMeta

class System(metaclass=SingletonMeta):

    __DEFAULT_SCREEN_SIZE = "1100,750"
    __width = -1
    __height = -1
    __rotation = -1
    __system_uuid = ""
    __cpu_count = None
    __cpu_assignments = None

    def get_screen_width(self) -> int:
        if self.__width > -1:
            return self.__width
        
        screen_size = self._get_screen_size()

        if "," in screen_size:            
            rotation = self.get_screen_rotation()
            if rotation == 0 or rotation == 180:
                self.__width = int(screen_size.split(',')[0])
            else: 
                self.__width = int(screen_size.split(',')[1])

            return self.__width
        
        return 1024
    
    def get_screen_height(self):
        if self.__height > -1:
            return self.__height
        
        screen_size = self._get_screen_size()

        if "," in screen_size:            
            rotation = self.get_screen_rotation()
            if rotation == 0 or rotation == 180:
                self.__height = int(screen_size.split(',')[1])
            else: 
                self.__height = int(screen_size.split(',')[0])

            return self.__height
        
        return 768

    def get_screen_rotation(self) -> int:
        if self.__rotation > -1:
            return self.__rotation
        
        try:
            res = subprocess.run(["xenstore-read", "/local/domain/system/screen_rotation"], capture_output=True, text=True, check=False)
            if res.returncode == 0:
                return int(res.stdout)
        except Exception:
            return 0
        
        return 0

    def _get_screen_size(self) -> str:
        try:
            res = subprocess.run(["xenstore-read", "/local/domain/system/screen_size"], capture_output=True, text=True, check=False)
            if res.returncode == 0:
                return res.stdout
        except Exception:
            return self.__DEFAULT_SCREEN_SIZE    
        
        return self.__DEFAULT_SCREEN_SIZE
    
    def get_system_uuid(self):
        system = platform.system().lower()

        # If we have it in cache...
        if self.__system_uuid != "":
            return self.__system_uuid
        
        if system == 'linux':
            try:
                with open('/sys/class/dmi/id/product_uuid', 'r') as f:
                    self.__system_uuid = f.read().strip()
            except FileNotFoundError:
                return ""  # UUID non disponible sur cette machine Linux
        
        elif system == 'windows':
            try:
                output = subprocess.check_output('wmic csproduct get uuid', shell=True)
                lines = output.decode().split('\n')
                uuid = [line.strip() for line in lines if line.strip() and "UUID" not in line]
                self.__system_uuid = uuid[0] if uuid else ""
            except subprocess.CalledProcessError:
                return ""  # Erreur lors de l'exécution de wmic
        
        elif system == 'darwin':  # macOS
            try:
                output = subprocess.check_output('ioreg -rd1 -c IOPlatformExpertDevice', shell=True)
                for line in output.decode().split('\n'):
                    if 'IOPlatformUUID' in line:
                        self.__system_uuid = line.split('"')[-2]
                return ""
            except subprocess.CalledProcessError:
                return ""  # Erreur lors de l'exécution de ioreg
        
        return self.__system_uuid

    def get_platform_cpu_count(self):
        if self.__cpu_count is not None:
            return self.__cpu_count
        
        try:
            output = subprocess.check_output(['xl', 'info'], encoding='utf-8')
            for line in output.splitlines():
                if line.startswith('nr_cpus'):
                    self.__cpu_count = int(line.split(':')[1].strip())
            return 1
        except Exception:
            return 12


    @staticmethod
    def debug_activated():
        try:
            fd = os.open("/proc/cmdline", os.O_RDONLY)
            data = os.read(fd)
            return b'debug=on' in data.lower()
        except Exception:
            return False
        
    @staticmethod
    def domain_name():
        return platform.node()
    

    @staticmethod
    def get_topology(override_topology_file:str = "") -> dict:
        """ Returns the topology of the current system

        The topology structure is different from the configuration file topology.json because the file will
        evolve from its original format and it must be dissociated from the internal structure to avoid
        future compatibility problems.

        The topology is defined in the file `topology.json`. This function returns a data structure
        representing the topology as a dict. Instead of returning the JSON data as the function 
        :func:`read_topology_file` does, it returns a structure representing the objects::

            >>> {
            >>>     "domains": [
            >>>         "my-domain": {
            >>>             "vcpu_group": "group1",
            >>>             "memory": 4000,
            >>>             "vcpus": 2,
            >>>             "cpus": "3-4",
            >>>             "package": ""
            >>>         }
            >>>     ],
            >>>     "system": {
            >>>         "use_usb": 1,
            >>>         "use_gui": 1,
            >>>         "screen_rotation": 0,
            >>>         "gui_app_package": "",
            >>>         "gui_memory": 1000,
            >>>     }
            >>> }
        """        

        topo_struct = {}
        topo_data = System.get_topology_data(override_topology_file)
        if topo_data is None:
            print("No topology data available. Aborting")
            return {}

        usb = topo_data.get("usb", {})
        gui = topo_data.get("gui", {})
        screen = gui.get("screen", {})
        vcpu = topo_data.get("vcpu", {})
        business = topo_data.get("business", {})
        business_domains = business.get("domains", [])

        use_usb = usb.get("use", False)
        use_gui = gui.get("use", False)
        gui_app_package = gui.get("app-package", "")
        screen_rotation = screen.get("rotation", 0)
                
        topo_struct["system"] = {
            "use_usb": use_usb,
            "use_gui": use_gui,
            "screen_rotation": screen_rotation,
            "gui_app_package": gui_app_package
        }

        vcpu_groups = vcpu.get("groups", {})

        topo_domains = {}
        for domain in business_domains:
            # Business domains
            domain_name = domain.get("name", "unknown")
            group_name = domain.get("vcpu_group", "")
            topo_domains[domain_name] = {
                "name": domain.get("name", "unknown"),
                "type": "business",
                "memory": domain.get("memory", 0),
                "package": domain.get("package", ""),
                "vcpus": System.compute_vcpus_for_group(group_name, vcpu_groups),
                "cpus": System().compute_cpus_for_group(group_name, vcpu_groups)
            }

        # sys-usb domain
        topo_domains["sys-usb"] = {
            "name": "sys-usb",
            "type": "core",
            "memory": 300,
            "vcpus": System.compute_vcpus_for_group("sys-usb", vcpu_groups),
            "cpus": System().compute_cpus_for_group("sys-usb", vcpu_groups)
        }

        # sys-gui domain
        topo_domains["sys-gui"] = {
            "name": "sys-gui",
            "type": "core",
            "memory": gui.get("memory"),
            "vcpus": System.compute_vcpus_for_group("sys-gui", vcpu_groups),
            "cpus": System().compute_cpus_for_group("sys-gui", vcpu_groups),            
        }

        topo_struct["domains"] = topo_domains

        return topo_struct


    @staticmethod
    def read_topology_file(override_topology_file:str = "") -> str:
        try:
            with open('/etc/psec/topology.json' if override_topology_file == "" else override_topology_file, 'r') as f:
                topo = f.read()
                f.close()
                return topo
        except Exception as e:
            print("An error occured while reading the file /etc/psec/topology.json")
            print(e)
            return ""

    @staticmethod
    def get_topology_data(override_topology_file:str = "") -> dict:
        try:
            topo_data = System.read_topology_file(override_topology_file)
            data = json.loads(topo_data)
            return data
        except Exception as e:
            print("An error occured while decoding JSON file")
            print(e)
            return None
        

    @staticmethod
    def compute_vcpus_for_group(group_name:str, groups:dict) -> int:
        """ Computes the number of vCPUs which will be pinned to each Domain of a group.

        The number of vCPUs depends on the value of the parameter vcpu.groups defined in the file topology.json.
        """
        vcpus = 1
        platform_cpus = System().get_platform_cpu_count()
        dom0_vcpus = 2 if platform_cpus > 4 else 1
        sys_usb_vcpus = 0 #Dom0 and sys-usb share the same vcpus

        if group_name == "sys-usb":
            return dom0_vcpus
        
        reserved_vcpus = dom0_vcpus + sys_usb_vcpus

        if group_name in groups.keys():
            vcpu_rate = groups.get(group_name, None)

            # Override cpu rate for sys-gui if not provided
            vcpu_rate = 0.2 if vcpu_rate is None and group_name == "sys-gui" else vcpu_rate

            if vcpu_rate is not None:
                vcpus = int(round(vcpu_rate*(platform_cpus-reserved_vcpus), 0))
 
                return max(vcpus, 1)

        return vcpus

    def compute_cpus_for_group(self, group_name:str, groups:dict) -> int:
        """ Computes the CPUs (or cores) which will be pinned to the Domains of the group.

        The first CPU is assigned to Dom0 and sys-usb Domain. 
        If there are at least 4 CPUs the second CPU is also assigned to Dom0 and sys-usb.
        The other CPUs are assigned to sys-gui and the other groups by trying to avoid overlapping.
        """
        
        if self.__cpu_assignments is not None:
            # If the groups are in cache we take them
            cpu_assignments = self.__cpu_assignments
        else:
            # Otherwise we calculate them before
            cpu_assignments = {
                "Dom0": [ 0 ],
                "sys-usb": [ 0 ]
            }

            next_pin = 1
            cpu_count = System().get_platform_cpu_count()
            if cpu_count > 4:
                # If there are more than 4 CPUs/cores we add one to Dom0 and sys-usb
                cpu_assignments["Dom0"].append(next_pin)
                cpu_assignments["sys-usb"].append(next_pin)
                next_pin += 1

            # Then we assign sys-gui
            if cpu_count < 2:
                cpu_assignments["sys-gui"] = [ 1 ] # sys-usb is shared with sys-gui
            elif cpu_count > 4:
                vcpus = System.compute_vcpus_for_group("sys-gui", groups)
                cpu_assignments["sys-gui"] = list(range(2, next_pin + vcpus))
                next_pin += 2

            # Then the other groups
            for group_name in groups.keys():
                vcpus = System.compute_vcpus_for_group(group_name, groups)
                cpu_assignments[group_name] = list(range(next_pin, next_pin + vcpus))

            self.__cpu_assignments = cpu_assignments

        # Finally we return the value
        return cpu_assignments.get(group_name, 1)

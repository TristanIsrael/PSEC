import json, sys, subprocess, multiprocessing
from configparser import ConfigParser
import os

class DomainsFactory:
    topology:dict = None
    xen_conn = None
    #alpine_repo = ""

    def __init__(self, topology:dict):
        self.topology = topology
        self.__cpu_count = os.cpu_count()
        #self.alpine_repo = alpine_repo

    def create_domains(self):
        print("Start creating domains from topology")

        usb = self.topology.get("usb")
        if usb != None and usb.get("use") == 1:
            self.__provision_domain("sys-usb", "psec-sys-usb", "lts")
            self.__create_domd_usb()

        gui = self.topology.get("gui")
        if gui != None and gui.get("use") == 1:
            package = gui.get("app-package")            
            self.__provision_domain("sys-gui", "psec-sys-gui" if package is None else package)
            self.__create_domd_gui()
            self.__fetch_alpine_packages(package)

        business = self.topology.get("business")
        if business != None:
            self.__parse_business_domains(business)
            

    ###
    # Private functions
    #
    def __create_domd_usb(self):
        print("Create Driver Domain USB")

        conf = self.__create_domain_sys_usb(memory_in_mb=500, nb_cpus=4 if self.__cpu_count >= 4 else min(self.__cpu_count /2, 1))

        if conf is not None:
            with open('/etc/psec/xen/sys-usb.conf', 'w') as f:
                f.write(conf)

    def __create_domd_gui(self):
        print("Create Driver Domain GUI")
        
        max_memory = self.get_max_memory_size()
        rotation = 0
        json_gui = self.topology.get("gui")
        if json_gui != None:
            json_memory = json_gui.get("memory")
            if json_memory != None:
                memory = json_memory
                print(f"Setting {memory} MB for memory")

        conf = self.__create_domain_sys_gui(memory_in_mb=memory, nb_cpus=4 if self.__cpu_count >= 4 else min(self.__cpu_count /2, 1))

        if conf is not None:
            with open('/etc/psec/xen/sys-gui.conf', 'w') as f:
                f.write(conf)
    
    def __parse_business_domains(self, json:dict):
        repository = json.get("repository")
        if repository is not None:
            pass # Todo

        domains = json.get("domains")
        if domains is not None:
            for domain in domains:
                name = domain.get("name")
                package = domain.get("app-package")
                memory = self.get_max_memory_size()
                if domain.get("memory") is not None:
                    memory = domain.get("memory")
                
                cpus = 1
                cpu_rate = domain.get("cpu", 1)
                if cpu_rate > 1:
                    cpu_rate = 1
                cpu_count = multiprocessing.cpu_count()
                cpus = round(cpu_count*cpu_rate)

                self.__provision_domain(name, package)
                conf = self.__create_new_domain(
                    domain_name= name,
                    memory_in_mb= memory,
                    nb_cpus= 1 if cpus == 0 else cpus,
                    boot_iso_location= f"bootiso-{name}.iso",
                    share_packages= True,
                    share_storage= True,
                    share_system= False
                    #rxtx_inputs= False
                )

                with open(f"/etc/psec/xen/{name}.conf", 'w') as f:
                    f.write(conf)

                self.__fetch_alpine_packages(package)     

    def __create_domain_sys_usb(self, memory_in_mb:int, nb_cpus:int) -> None:
        txt = '''
type = "pv"
name = "sys-usb"
kernel = "/var/lib/xen/boot/vmlinuz-lts"
ramdisk = "/var/lib/xen/boot/initramfs-lts"
extra = "modules=loop,squashfs,iso9660 console=hvc0 module_blacklist=af_packet,network,video,sound,drm,snd,snd_hda_intel,bluetooth,btusb,r8153_ecm,r8152,usbnet,uvcvideo,pcspkr,videobuf2_v4l2,joydev,videodev,videobuf2_common,libphy,mc,mii"
memory={}
vcpus = {}
disk = [
	'format=raw, vdev=xvdc, access=r, devtype=cdrom, target=/usr/lib/psec/system/bootiso-sys-usb.iso'
]
p9 = [
'tag=packages, path=/usr/lib/psec/packages, backend=0, security_model=none',
'tag=storage, path=/usr/lib/psec/storage, backend=0, security_model=none',
'tag=system, path=/usr/lib/psec/system, backend=0, security_model=none'
]
channel = [
'name=sys-usb-msg, connection=socket, path=/var/run/sys-usb-msg.sock',
'name=sys-usb-input, connection=socket, path=/var/run/sys-usb-input.sock',
'name=sys-usb-tty, connection=socket, path=/var/run/sys-usb-tty.sock'
]
device_model_override = "/usr/bin/qemu-system-x86_64"
device_model_version = "qemu-xen"
vnc=0
'''.format(memory_in_mb, nb_cpus)

        return txt

    def __create_domain_sys_gui(self, memory_in_mb:int, nb_cpus:int) -> None:
        max_memory = self.get_max_memory_size()

        txt = '''
type = "hvm"
name = "sys-gui"
memory={}
vcpus = {}
disk = [
	'format=raw, vdev=xvdc, access=r, devtype=cdrom, target=/usr/lib/psec/system/bootiso-sys-gui.iso'
]
p9 = [
    'tag=packages, path=/usr/lib/psec/packages, backend=0, security_model=none',
    'tag=storage, path=/usr/lib/psec/storage, backend=0, security_model=none',
    'tag=system, path=/usr/lib/psec/system, backend=0, security_model=none'
]
channel = [
'name=sys-gui-msg, connection=socket, path=/var/run/sys-gui-msg.sock',
'name=sys-gui-input, connection=socket, path=/var/run/sys-gui-input.sock'
]
vga = "none"
device_model_override = "/usr/bin/qemu-system-x86_64"
device_model_version = "qemu-xen"
device_model_args = [
     '-device', 'virtio-gpu-pci',
     '-display', 'gtk,full-screen=on,zoom-to-fit=on,gl=on',
     '-device', 'virtio-input-host,id=virtio-mouse,evdev=/dev/input/virtual_mouse',
     '-device', 'virtio-input-host,id=virtio-touch,evdev=/dev/input/virtual_touch'
]
usb=0
vnc=0
vif=[]
'''.format(memory_in_mb, nb_cpus)

        return txt

    def __create_new_domain(self, domain_name:str, memory_in_mb:int, nb_cpus:int, boot_iso_location:str, share_packages:bool=True, share_storage:bool=True, share_system:bool=False):
        txt = '''
type = "pv"
name = "{}"
kernel = "/var/lib/xen/boot/vmlinuz-virt"
ramdisk = "/var/lib/xen/boot/initramfs-virt"
extra = "modules=loop,squashfs,iso9660 console=hvc0  module_blacklist=af_packet,network,video,sound,drm,snd,snd_hda_intel,bluetooth,btusb,r8153_ecm,r8152,usbnet,uvcvideo,pcspkr,videobuf2_v4l2,joydev,videodev,videobuf2_common,libphy,mc,mii"
memory={}
vcpus = {}
disk = [
	'format=raw, vdev=xvdc, access=r, devtype=cdrom, target=/usr/lib/psec/system/{}'
]
device_model_override = "/usr/bin/qemu-system-x86_64"
device_model_version = "qemu-xen"
vnc=0
'''.format(domain_name, memory_in_mb, nb_cpus, boot_iso_location)
        
        # Add P9 shares
        shares = []
        if share_packages:
            shares.append("'tag=packages, path=/usr/lib/psec/packages, backend=0, security_model=none'")
        if share_storage:
            shares.append("'tag=storage, path=/usr/lib/psec/storage, backend=0, security_model=none'")
        if share_system:
            shares.append("'tag=system, path=/usr/lib/psec/system, backend=0, security_model=none'")

        if len(shares) > 0:
            txt += "p9 = [\n{}\n]\n".format(",\n".join(shares))

        # Add serial channels
        channels = []
        channels.append(f"'name={domain_name}-msg, connection=socket, path=/var/run/{domain_name}-msg.sock'") # /dev/hvc1
        
        if len(channels) > 0:
            txt += "channel = [\n{}\n]\n".format(",\n".join(channels))

        return txt

    def __provision_domain(self, domain_name:str, main_package:str, alpine_branch:str = "virt"):
        cmd = "/usr/lib/psec/bin/provision-domain.sh"

        try:
            subprocess.run([cmd, domain_name, main_package, alpine_branch], check=True)
        except Exception as e:
            print("An error occured during domain provisioning")
            print(e)    

    def __fetch_alpine_packages(self, package):
        # Fetch Alpine packages   
        if package is None:
            print("Error: package is empty")

        subprocess.run(
            args= ["apk", "fetch", "-R", package], 
            cwd= "/usr/lib/psec/packages/alpine/x86_64",
            check= True
        )

        subprocess.run(
            args= ["/usr/lib/psec/bin/reindex-and-sign-repository.sh"], 
            check= True
        )  

    def get_max_memory_size(self) -> int:
        ''' Returns the default memory size for a Domain

        When not specified, the memory size is 90% of the system memory
        '''

        memory = 1024

        try:
            result = subprocess.run(['python3', '/usr/lib/psec/bin/get-total-memory.py'], capture_output=True, text=True)            
            memory = int(result.stdout)
            print(f"Memory detected: {memory} MB")

            # Then we apply a 90% factor
            memory *= 0.9
        except:
            print("Impossible d'obtenir la quantité de mémoire disponible sur le système")

        return round(memory)

###
### Local functions
def read_topology_file() -> str:
    try:
        with open('/etc/psec/topology.json', 'r') as f:
            topo = f.read()
            f.close()
            return topo
    except Exception as e:
        print("An error occured while reading the file /etc/psec/topology.json")
        print(e)
        return ""

def decode_topology_data(data:str) -> dict:
    try:
        data = json.loads(data)
        return data
    except Exception as e:
        print("An error occured while decoding JSON file")
        print(e)
        return None    

###
### Entry point
if __name__ == "__main__":
    print("Starting Domains creation process")

    print("Open topology file")
    f = read_topology_file()

    print("Decode topology file")
    topology = decode_topology_data(f)

    print("Start topology factory")
    #alpine_repo = sys.argv[1]
    factory = DomainsFactory(topology)
    factory.create_domains()
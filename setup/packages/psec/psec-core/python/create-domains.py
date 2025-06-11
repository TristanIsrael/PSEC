import json, sys, subprocess, multiprocessing
from configparser import ConfigParser
from psec import System
import os

class DomainsFactory:
    __topology:dict = {}

    def __init__(self, topology:dict):
        self.__topology = topology

    def create_domains(self):
        print("Start creating domains from topology")

        system = self.__topology.get("system", {})
        use_usb = system.get("use_usb", False)
        use_gui = system.get("use_gui", False)

        if use_usb:
            self.__provision_domain("sys-usb", "psec-sys-usb", "lts")
            self.__create_domd_usb()

        if use_gui:
            package = system.get("gui_app_package")
            self.__provision_domain("sys-gui", "psec-sys-gui" if package is None else package)
            self.__create_domd_gui()
            self.__fetch_alpine_packages(package)
        
        self.__provision_business_domains()
            

    ###
    # Private functions
    #
    def __create_domd_usb(self):
        print("Create Driver Domain USB")

        conf = self.__create_domain_sys_usb()

        if conf is not None:
            with open('/etc/psec/xen/sys-usb.conf', 'w') as f:
                f.write(conf)


    def __create_domd_gui(self):
        print("Create Driver Domain GUI")

        conf = self.__create_domain_sys_gui()

        if conf is not None:
            with open('/etc/psec/xen/sys-gui.conf', 'w') as f:
                f.write(conf)
    
    def __provision_business_domains(self):
        domains = self.__topology.get("domains", {})
        if domains is not None:
            for domain_name in domains:
                config = domains[domain_name]
                domain_type = config.get("type")

                if domain_type != "business":
                    continue

                package = config.get("package")

                self.__provision_domain(domain_name, package)
                conf = self.__create_new_domain(
                    domain_name= domain_name,                    
                    boot_iso_location= f"bootiso-{domain_name}.iso",
                    share_packages= True,
                    share_storage= True,
                    share_system= False
                )

                with open(f"/etc/psec/xen/{domain_name}.conf", 'w') as f:
                    f.write(conf)

                self.__fetch_alpine_packages(package)

    def __create_domain_sys_usb(self) -> None:
        domains = self.__topology.get("domains", {})
        sys_usb = domains.get("sys-usb", {})

        txt = f'''
type = "hvm"
name = "sys-usb"
memory= { sys_usb.get("memory") }
vcpus = { sys_usb.get("vcpus") }
cpus = "{ self.__cpus_list_to_string(sys_usb.get("cpus", [])) }"
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
vga = "none"
device_model_override = "/usr/bin/qemu-system-x86_64"
device_model_version = "qemu-xen"
usb=0
vnc=0
vif=[]
'''

        return txt

    def __create_domain_sys_gui(self) -> None:
        domains = self.__topology.get("domains", {})
        sys_gui = domains.get("sys-gui", {})

        txt = f'''
type = "hvm"
name = "sys-gui"
memory={ sys_gui.get("memory", 512 ) }
vcpus = { sys_gui.get("vcpus") }
cpus = "{ self.__cpus_list_to_string(sys_gui.get("cpus", [])) }"
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
'''

        return txt

    def __create_new_domain(self, domain_name:str, boot_iso_location:str, share_packages:bool=True, share_storage:bool=True, share_system:bool=False):
        domains = self.__topology.get("domains", {})
        dom = domains.get(domain_name, {})

        print("domain:", domain_name, "cpus=", dom.get("cpus"))

        txt = f'''
type = "pv"
name = "{ domain_name }"
kernel = "/var/lib/xen/boot/vmlinuz-virt"
ramdisk = "/var/lib/xen/boot/initramfs-virt"
extra = "modules=loop,squashfs,iso9660 console=hvc0  module_blacklist=af_packet,network,video,sound,drm,snd,snd_hda_intel,bluetooth,btusb,r8153_ecm,r8152,usbnet,uvcvideo,pcspkr,videobuf2_v4l2,joydev,videodev,videobuf2_common,libphy,mc,mii"
memory = { dom.get("memory", 512) }
vcpus = { dom.get("vcpus") }
cpus = "{ self.__cpus_list_to_string(dom.get("cpus", [])) }"
disk = [
	'format=raw, vdev=xvdc, access=r, devtype=cdrom, target=/usr/lib/psec/system/{boot_iso_location}'
]
device_model_override = "/usr/bin/qemu-system-x86_64"
device_model_version = "qemu-xen"
vnc=0
'''
        
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

###
### Local functions
    def __cpus_list_to_string(self, cpus:list) -> str:
        if not cpus:
            return "0"
        elif len(cpus) == 1:
            return str(cpus[0])
        return f"{cpus[0]}-{cpus[-1]}"

###
### Entry point
if __name__ == "__main__":
    print("Starting Domains creation process")

    print("Decode topology file")
    topology = System.get_topology()

    print("Start topology factory")
    #alpine_repo = sys.argv[1]
    factory = DomainsFactory(topology)
    factory.create_domains()
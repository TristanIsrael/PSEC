import json 
from configparser import ConfigParser
import subprocess

class DomainsFactory:
    topology:dict = None
    xen_conn = None

    def __init__(self, topology:dict):
        self.topology = topology    

    def create_domains(self):
        print("Start creating domains from topology")

        usb = self.topology.get("usb")
        if usb != None and usb.get("use") == 1:
            self.__provision_domain("sys-usb", "psec-sys-usb")
            self.create_domd_usb()

        gui = self.topology.get("gui")
        if gui != None and gui.get("use") == 1:
            self.__provision_domain("sys-gui", "psec-sys-gui")
            self.create_domd_gui()
            

    def create_domd_usb(self):
        print("Create Driver Domain USB")

        conf = self.__create_new_domain(
            domain_name="sys-usb", 
            memory_in_mb=400,
            nb_cpus=1, 
            boot_iso_location="bootiso-sys-usb.iso",
            share_packages=True,
            share_storage=True,
            share_system=True,
            rxtx_inputs=True,
            pci_passthrough=True
        )

        with open('/etc/psec/xen/sys-usb.conf', 'w') as f:
            f.write(conf)

    def create_domd_gui(self):
        print("Create Driver Domain GUI")

        conf = self.__create_new_domain(
            domain_name="sys-gui", 
            memory_in_mb=400,
            nb_cpus=1, 
            boot_iso_location="bootiso-sys-gui.iso",
            share_packages=True,
            share_storage=True,
            share_system=True,
            rxtx_inputs=True,
            pci_passthrough=False,
            vga_passthrough=True
        )

        with open('/etc/psec/xen/sys-gui.conf', 'w') as f:
            f.write(conf)

    # Private functions
    def __create_new_domain(self, domain_name:str, memory_in_mb:int, nb_cpus:int, boot_iso_location:str, share_packages:bool, share_storage:bool, share_system:bool=False, rxtx_inputs:bool=False, pci_passthrough:bool=False, vga_passthrough:bool=False):
        txt = '''
type = "pv"
name = "{}"
kernel = "/var/lib/xen/boot/vmlinuz-virt"
ramdisk = "/var/lib/xen/boot/initramfs-virt"
extra = "modules=loop,squashfs,iso9660 console=hvc0"
memory={}
vcpus = {}
disk = [
	'format=raw, vdev=xvdc, access=r, devtype=cdrom, target=/usr/lib/psec/system/{}'
]
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
        channels.append("'name=console, connection=pty'")
        channels.append("'name={}-msg, connection=socket, path=/var/run/{}-msg.sock'".format(domain_name, domain_name))
        channels.append("'name={}-log, connection=socket, path=/var/run/{}-log.sock'".format(domain_name, domain_name))
        if rxtx_inputs:
            channels.append("'name={}-input, connection=socket, path=/var/run/{}-input.sock'".format(domain_name, domain_name))
        
        if len(channels) > 0:
            txt += "channels = [\n{}\n]\n".format(",\n".join(channels))        
        
        parser=ConfigParser()
        with open("/etc/conf.d/xen-pci") as stream:
            parser.read_string("[none]\n" +stream.read())

            # Add PCI passthrough
            if pci_passthrough and parser["none"]["DEVICES"] != None:
                devs = parser["none"]["DEVICES"]

                if devs != "" and devs != None:
                    txt += "pci = [{}]\n".format(devs.replace(' ', '","'))

            # Add VGA passthrough
            if vga_passthrough and parser["none"]["VGA_DEVICES"] != None:
                devs = parser["none"]["VGA_DEVICES"]

                if devs != "" and devs != None:
                    txt += "pci = [{}]\n".format(devs.replace(' ', '", "'))

        return txt

    def __provision_domain(self, domain_name:str, main_package:str):
        cmd = "/usr/lib/psec/bin/provision-domain.sh"

        try:
            subprocess.run([cmd, domain_name, main_package], check=True)
        except Exception as e:
            print("An error occured during domain provisioning")
            print(e)

###
### Local functions
def read_topology_file() -> str:
    try:
        with open('/etc/psec/topology.json', 'r') as f:
            return f.read()
    except Exception as e:
        print("An error occured while reading the file /etc/psec/topology.json")
        print(e)
        return ""
    finally:
        f.close()     

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
    factory = DomainsFactory(topology)
    factory.create_domains()
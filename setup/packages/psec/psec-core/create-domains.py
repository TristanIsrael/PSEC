import json, sys, subprocess, multiprocessing
from configparser import ConfigParser

class DomainsFactory:
    topology:dict = None
    xen_conn = None
    alpine_repo = ""

    def __init__(self, topology:dict, alpine_repo:str):
        self.topology = topology    
        self.alpine_repo = alpine_repo

    def create_domains(self):
        print("Start creating domains from topology")

        usb = self.topology.get("usb")
        if usb != None and usb.get("use") == 1:
            self.__provision_domain("sys-usb", "psec-sys-usb")
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

    def __create_domd_gui(self):
        print("Create Driver Domain GUI")

        memory = 1024
        json_gui = self.topology.get("gui")
        if json_gui != None:
            json_memory = json_gui.get("memory")
            if json_memory != None:
                memory = json_memory
                print("Setting {} MB for memory".format(memory))

        conf = self.__create_new_domain(
            domain_name="sys-gui", 
            memory_in_mb=memory,
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
    
    def __parse_business_domains(self, json:dict):
        repository = json.get("repository")
        if repository != None:
            pass # Todo

        domains = json.get("domains")
        if domains != None:
            for domain in domains:
                name = domain.get("name")
                package = domain.get("package")
                memory = domain.get("memory")
                
                cpus = 1
                cpu_rate = domain.get("cpu")
                cpu_count = multiprocessing.cpu_count()
                cpus = round(cpu_count*cpu_rate)

                self.__provision_domain(name, package)
                conf = self.__create_new_domain(
                    domain_name= name,
                    memory_in_mb= memory,
                    nb_cpus= 1 if cpus == 0 else cpus,
                    boot_iso_location= "bootiso-{}.iso".format(name),
                    share_packages= True,
                    share_storage= True,
                    share_system= False,
                    rxtx_inputs= False,
                    pci_passthrough= False,
                    vga_passthrough= False
                )

                with open("/etc/psec/xen/{}.conf".format(name), 'w') as f:
                    f.write(conf)

                self.__fetch_alpine_packages(package)     

    def __create_new_domain(self, domain_name:str, memory_in_mb:int, nb_cpus:int, boot_iso_location:str, share_packages:bool=True, share_storage:bool=True, share_system:bool=False, rxtx_inputs:bool=False, pci_passthrough:bool=False, vga_passthrough:bool=False):
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
            txt += "channel = [\n{}\n]\n".format(",\n".join(channels))        
        
        if pci_passthrough != None and vga_passthrough != None:
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

    def __fetch_alpine_packages(self, package):
        # Fetch Alpine packages                
        subprocess.run(
            args= ["apk", "fetch", "-R", package], 
            cwd= alpine_repo,
            check= True
        )

        subprocess.run(
            args= ["/usr/lib/psec/bin/reindex-and-sign-repository.sh"], 
            check= True
        )  

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

    if len(sys.argv) < 2:
        print("Error: missing argument alpine_repository_location")
        exit(2)

    print("Open topology file")
    f = read_topology_file()

    print("Decode topology file")
    topology = decode_topology_data(f)

    print("Start topology factory")
    alpine_repo = sys.argv[1]
    factory = DomainsFactory(topology, alpine_repo)
    factory.create_domains()
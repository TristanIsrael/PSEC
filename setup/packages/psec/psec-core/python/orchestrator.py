from psec import MqttFactory, Logger, TypeEntree, Topics, ResponseFactory
import os
import glob
import subprocess
import evdev
import time
import socket
import msgpack
import threading
import json
from evdev import InputDevice, ecodes, UInput

mqtt_lock = threading.Event()
mqtt = MqttFactory.create_mqtt_client_dom0("Orchestrator")
MOUSE_NAME="PSEC virtual mouse"
TOUCH_NAME="PSEC virtual touchscreen"
INPUTS_SOCKET="/var/run/sys-usb-input.sock"
VIRTUAL_MOUSE_PATH="/dev/input/virtual_mouse"
VIRTUAL_TOUCH_PATH="/dev/input/virtual_touch"
CREATE_DOMAINS=True


def find_touchscreen() -> InputDevice:
    inputs = glob.glob("/dev/input/event*")
    for input in inputs:
        #print("Fichier {}".format(input))
        
        try:          
            dev = InputDevice(input)
            caps = dev.capabilities()
            #print(caps)
            
            if ecodes.EV_ABS in caps:                            
                # We get all the capabilities
                Logger().debug("Found a touchscreen: {}".format(dev.name))
                return dev
        except Exception as e:
            print(e)
            continue

    return None

def get_device_path(devname:str) -> str:
    for device_path in evdev.list_devices():
        device = evdev.InputDevice(device_path)

        if device.name == devname:
            return device.path
        
    return ""

def create_virtual_mouse():
    capabilities = {
        ecodes.EV_KEY: [ecodes.BTN_LEFT, ecodes.BTN_RIGHT],
        ecodes.EV_REL: [ecodes.REL_X, ecodes.REL_Y, ecodes.REL_WHEEL, ecodes.REL_WHEEL_HI_RES],
    }

    input = UInput(capabilities, name=MOUSE_NAME)
    Logger().debug("Created virtual mouse {}".format(input.name))
    return input

def create_virtual_touch(touch_device) -> InputDevice:
    virtual_touch = UInput.from_device(touch_device, name=TOUCH_NAME)
    Logger().debug("Created virtual touchscreen {}".format(virtual_touch.name))
    return virtual_touch

def start_events_listener(virtual_mouse, virtual_touch):
    Logger().debug("Start input listener")
    print("Start input listener")
    buffer = bytearray()

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(INPUTS_SOCKET)
    while True:
        raw_data = sock.recv(128)
        buffer.extend(raw_data)

        while b'\n' in buffer:
            # Trouver la première occurrence du délimiteur '\n'
            delim_pos = buffer.find(b'\n')

            # Extraire la trame complète jusqu'au délimiteur
            frame = buffer[:delim_pos]

            # Supprimer la trame du tampon
            buffer = buffer[delim_pos + 1:]

            try:
                # Désérialiser la trame avec Msgpack
                data = msgpack.unpackb(frame)

                # Supposons que 'data' soit un tableau de 4 entiers
                device_type, event_type, event_code, event_value = data

                if device_type == TypeEntree.SOURIS:
                    input = virtual_mouse
                elif device_type == TypeEntree.TOUCH and virtual_touch is not None:
                    input = virtual_touch
                else:
                    input = None

                if input is not None:
                    input.write(event_type, event_code, event_value)                
                    input.syn()

            except Exception as e:
                print(f"Erreur lors du traitement de la trame : {e}")

def wait_for_file(filepath):
    print("Wait for the domains to be created")

    while not os.path.exists(filepath):
        time.sleep(0.5)


def get_blacklisted_devices():
    with open("/etc/psec/topology.json", 'r') as file:
        data = json.load(file)

        pci = data.get("pci", {})
        blacklist = pci.get("blacklist", "")
        return blacklist.split(",")

    return []


def get_pci_usb_devices():
    devs = []
    
    cmd = subprocess.run(["lspci"], capture_output=True)
    if cmd.returncode == 0:
        spl = cmd.stdout.split(b'\n')

        for dev in spl:
            if "USB" in dev.decode():
                dev_id = dev.split(b' ')[0]
                if dev_id not in devs:
                    devs.append(dev_id.decode())

    return devs


def is_blacklisted(dev:str, blacklist:list):
    for d in blacklist:
        if dev.endswith(d):
            return True
        
    return False


def expose_pci_devices():
    blacklisted_devices = get_blacklisted_devices()
    pci_usb_devs = get_pci_usb_devices()

    #print(blacklisted_devices)
    #print(pci_usb_devs)

    whitelist = []
    for dev in pci_usb_devs:
        if is_blacklisted(dev, blacklisted_devices):
            Logger().debug("Device {} is ignored because it is blacklisted".format(dev))
        else:            
            Logger().debug("Expose device {}".format(dev))
            cmd = ["xl", "pci-assignable-add", dev]

            res = subprocess.run(cmd)
            if res.returncode == 0:
                Logger().debug("Device {} has been exposed to Xen".format(dev)) 
                whitelist.append(dev)
            else:
                Logger().error("There has been a error while exposing the device {} to Xen".format(dev))           
    
    # Append devices to sys-usb.conf
    if len(whitelist) > 0:
        patch_sys_usb_conf(whitelist)  


def patch_sys_usb_conf(usb_devs:list):
    with open("/etc/psec/xen/sys-usb.conf", 'r') as file:
        lines = file.readlines()
    filtered_lines = [line for line in lines if "pci =" not in line]

    filtered_lines.append("\n")
    filtered_lines.append("# USB devices attached to sys-usb\n")
    filtered_lines.append("pci = ['{}']\n".format("','".join(usb_devs)))

    with open("/etc/psec/xen/sys-usb.conf", "w") as file:
        file.writelines(filtered_lines)


def start_business_domains():
    try:
        with open('/etc/psec/topology.json', 'r') as f:
            data = json.loads(f.read())
            f.close()
            
        json_business = data.get("business", {})
        json_domains = json_business.get("domains", [])
        for domain in json_domains:
            domain_name = domain.get("name", "")
            if domain_name == "":
                continue 

            cmd = ["/usr/lib/psec/bin/start-business-domain.sh", domain_name]
            res = subprocess.run(cmd)

            if res == 0:
                Logger().info("Started Domain {}".format(domain_name))  
            else:                
                Logger().critical("Domain {} did not start".format(domain_name))            

    except Exception as e:
        print("An error occured while reading the file /etc/psec/topology.json")
        print(e)
        Logger().critical("Could not read the topology to start business Domains")


def on_mqtt_message(topic:str, payload:dict):
    if topic == "{}/request".format(Topics.SHUTDOWN):
        Logger().warn("System shutdown requested!")

        # There is currently no rule for the shutdown, so we accept it
        response = ResponseFactory.create_response_shutdown(True)
        mqtt.publish("{}/response".format(Topics.SHUTDOWN), response)

        # Then we whut the system down
        cmd = ["halt", "-d", "5"]
        subprocess.run(cmd)


def on_mqtt_ready():
    Logger().setup("Orchestrator", mqtt)
    Logger().info("Starting Orchestrator")

    mqtt.add_message_callback(on_mqtt_message)
    mqtt.subscribe("{}/+/request".format(Topics.WORKFLOW))    

    # Create virtual input devices
    virtual_mouse = create_virtual_mouse()
    # Create symlinks for the virtual inputs which act as a permalinks
    mouse_path = get_device_path(MOUSE_NAME)
    if mouse_path == "":
        Logger().error("The mouse device path has not been found")
    else:
        if os.path.exists(VIRTUAL_MOUSE_PATH) or os.path.islink(VIRTUAL_MOUSE_PATH):
            os.remove(VIRTUAL_MOUSE_PATH)
            time.sleep(0.1)
        os.symlink(mouse_path, VIRTUAL_MOUSE_PATH)

    # Find touch screen and keep capabilities
    touch_device = find_touchscreen()    
    if touch_device == None:
        Logger().info("No touchscreen found on the system")
        virtual_touch = None
    else:
        #print(touch_caps)
        virtual_touch = create_virtual_touch(touch_device)
        touch_path = get_device_path(TOUCH_NAME)
        if touch_path == "":
            Logger().error("The touch device path has not been found")
        else:
            if os.path.exists(VIRTUAL_TOUCH_PATH) or os.path.islink(VIRTUAL_TOUCH_PATH):
                os.remove(VIRTUAL_TOUCH_PATH)
                time.sleep(0.1)
            os.symlink(touch_path, "/dev/input/virtual_touch")    

    # Attach PCI devices
    expose_pci_devices() 

    # Start sys-usb
    if CREATE_DOMAINS:
        cmd = ["/usr/lib/psec/bin/start-sys-usb.sh"]
        res = subprocess.run(cmd)

        if res == 0:
            Logger().info("Started Domain sys-usb")  
        else:
            Logger().critical("Domain sys-usb did not start")  

        # Start sys-gui
        cmd = ["/usr/lib/psec/bin/start-sys-gui.sh"]
        res = subprocess.run(cmd)

        if res == 0:
            Logger().info("Started Domain sys-gui") 
        else:
            Logger().critical("Domain sys-gui did not start")

        # Start all other domains
        start_business_domains()

        # Wait for the inputs socket to be ready
        wait_for_file(INPUTS_SOCKET)

    # Start listening for events from sys-usb
    start_events_listener(virtual_mouse, virtual_touch)


if __name__ == "__main__":
    print("Starting PSEC orchestrator")
    
    mqtt.add_connected_callback(on_mqtt_ready)
    mqtt.start() 

    mqtt_lock.wait()

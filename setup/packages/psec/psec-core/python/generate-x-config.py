import json, subprocess


def angle_to_rotate(angle):
    mapping = {
        0: "normal",
        90: "left",
        -90: "right",
        180: "inverted"
    }
    return mapping.get(angle, "normal")


def write_monitor_section(angle:int) -> None:
    filepath = "/etc/X11/xorg.conf.d/10-monitor.conf"

    # Lecture de la résolution normale
    with open('/sys/class/graphics/fb0/virtual_size', 'r') as fichier:
        resolution = fichier.read().strip().replace(",", "x")
        #print(resolution)

    # Calcul de la résolution
    if resolution is None:
        resolution = "1024x768"

    #new_resolution = compute_resolution(resolution, angle)
    #print(new_resolution)

    # Commande pour appliquer la rotation
    section = """
Section "Monitor"
    Identifier "Monitor0"
    Option "PreferredMode" "{}"
    Option "Rotate" "{}" 
    Option "DPMS" "false"
EndSection
""".format(resolution, angle_to_rotate(angle))
            
    with open(filepath, "w") as fichier:
        fichier.write(section)

if __name__ == "__main__":
    print("Generate X server configuration files")

    # Rotation is defined in topology.json
    topology_file="/etc/psec/topology.json"

    try:
        with open(topology_file, 'r') as file:
            json_data = json.load(file)
    except Exception as e:
        print("An error occured while reading the topology file {}".format(topology_file))    
        print(e)    
        exit(1)    

    #"gui": {
    #    "use": 1,    
    #    "screen": {
    #        "rotation": 0
    json_gui = json_data.get("gui")
    if json_gui is None:
        print("No GUI in topology")
        exit(0)
        
    json_use = json_gui.get("use")
    if json_use is None:
        print("GUI is unset in topology")
        exit(0)

    json_screen = json_gui.get("screen")
    if json_screen is not None:        
        rotation = json_screen.get("rotation")
               
        write_monitor_section(rotation)
    
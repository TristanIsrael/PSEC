import sys, json, subprocess

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: missing argument domid")
        exit(1)

    domid = sys.argv[1]
    print("Write screen information into Xenstore for domain {}".format(domid))

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
    if json_screen is None:
        print("No screen option in topology")
        exit(0)

    rotation = json_screen.get("rotation")
    if rotation is None:
        print("No rotation in topology")
        exit(0)

    if rotation is None:
        rotation = 0

    command = "xenstore-write /local/domain/system/screen_rotation {}".format(rotation)

    subprocess.run(command, shell=True, check=True)
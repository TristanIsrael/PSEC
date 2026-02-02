from PIL import Image
import sys
import os
import json

LOGO_FILEPATH = "/boot/splash.png"
TOPOLOGY_FILE="/etc/psec/topology.json"
DEFAULT_BGCOLOR = "#1ca9f7"

def get_bgcolor():
    try:
        with open(TOPOLOGY_FILE, 'r') as file:
            json_data = json.load(file)

            json_product = json_data.get("product")
            
            if json_product is None:
                print("No product definition in topology")
                return DEFAULT_BGCOLOR

            # Read the backgroung color value
            json_bgcolor = json_product.get("splash_bgcolor")
            if json_bgcolor is None:
                print("There is no splash_bgcolor value in the topology. Using default")
                return DEFAULT_BGCOLOR
            
            return json_bgcolor
    except Exception as e:
        print("An error occured while reading the topology file {}".format(TOPOLOGY_FILE))    
        print(e)
        return DEFAULT_BGCOLOR

def create_splash(width:int, height:int) -> Image:
    print(f"Create splash of size {width}x{height}")

    splash = Image.new("RGB", (width, height), get_bgcolor())
    image = Image.open(LOGO_FILEPATH)
    
    image_width, image_height = image.size
    x = (width - image_width) // 2
    y = (height - image_height) // 2

    splash.paste(image, (x,y), image)

    return splash

def save_splash(splash:Image, dest:str):
    width, height = splash.size

    print("Create PNG file")
    splash.save(f"{dest}/splash_{width}_{height}.png")
    
    print("Create PPM file")
    splash.save(f"{dest}/splash_{width}_{height}.ppm", format="PPM")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: missing arguments")
        print("Usage: ")
        print(f"    {os.path.basename(__file__)} width height destination_dir")
        exit()

    width = int(sys.argv[1])
    height = int(sys.argv[2])
    dest = sys.argv[3]

    image = create_splash(width, height)
    save_splash(image, dest)


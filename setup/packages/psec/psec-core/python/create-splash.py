from PIL import Image
import sys
import os
import json
from psec import topology

LOGO_FILEPATH = "/boot/splash.png"
TOPOLOGY_FILE="/etc/psec/topology.json"

def create_splash() -> Image:
    width = topology.screen.width
    height = topology.screen.height

    print(f"Create splash of size {width}x{height}")

    splash = Image.new("RGB", (width, height), topology.colors["splash_bgcolor"])
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
    if len(sys.argv) < 1:
        print("Error: missing arguments")
        print("Usage: ")
        print(f"    {os.path.basename(__file__)} destination_dir")
        exit()
    
    dest = sys.argv[3]

    image = create_splash()
    save_splash(image, dest)


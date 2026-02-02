from PIL import Image
import sys
import os

LOGO_FILEPATH = "/boot/splash.png"

def create_splash(width:int, height:int) -> Image:
    print(f"Create splash of size {width}x{height}")

    splash = Image.new("RGB", (width, height), "#1ca9f7")
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


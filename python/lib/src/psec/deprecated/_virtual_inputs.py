import struct
import serial
import msgpack
import time

# Configuration du port série
SERIAL_PORT = "/dev/hvc2"  # Remplacez par le port série réel
BAUDRATE = 9600

# Taille d'une trame packée (a=uint8, b=uint16, c=uint16, d=int32)
FRAME_FORMAT = "<BHHi"  # 'B': uint8, 'H': uint16, 'I': int32
FRAME_SIZE = struct.calcsize(FRAME_FORMAT)  # Taille attendue de la trame (9 octets)

# Open the device file once
path_evdev_mouse = "/dev/input/event3"
evdev_mouse = open(path_evdev_mouse, "wb")
print("Opened evdev file for mouse")

def write_evdev(evdev_file, event_type, event_code, event_value):    
    try:        
        # Structure de la trame evdev (16 octets)
        #event_data = struct.pack("<llHHi", 0, 0, event_type, event_code, event_value)
        event_data = struct.pack('llHHi', 0, 0, event_type, event_code, event_value)
        evdev_file.write(event_data)
        evdev_file.flush()
    except FileNotFoundError:
        print(f"Fichier evdev non trouvé : {evdev_file}")
    except PermissionError:
        print(f"Permission refusée pour écrire dans {evdev_file}")

buffer = bytearray()
flush_interval = 0.1  # 100 millisecondes
last_flush_time = time.time()

# Ouverture du fichier evdev une seule fois en mode binaire
with open(path_evdev_mouse, "wb") as evdev_file:
    with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1) as ser:
        while True:
            raw_data = ser.read(256)
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

                    # Obtenir le timestamp actuel
                    '''tv_sec = int(time.time())  # secondes depuis l'époque Unix
                    tv_usec = int((time.time() % 1) * 1000000)  # microsecondes

                    # Créer l'événement evdev avec le timestamp et les données
                    event = bytearray()

                    # Ajouter le timestamp (tv_sec, tv_usec)
                    event.extend(tv_sec.to_bytes(4, byteorder='little'))  # tv_sec (4 octets)
                    event.extend(tv_usec.to_bytes(4, byteorder='little'))  # tv_usec (4 octets)

                    # Ajouter event.type (2 octets)
                    event.extend([event_type & 0xFF, (event_type >> 8) & 0xFF])

                    # Ajouter event.code (2 octets)
                    event.extend([event_code & 0xFF, (event_code >> 8) & 0xFF])

                    # Ajouter event.value (4 octets)
                    event.extend([event_value & 0xFF, (event_value >> 8) & 0xFF, 
                                (event_value >> 16) & 0xFF, (event_value >> 24) & 0xFF])

                    # Écrire l'événement dans le fichier evdev
                    evdev_file.write(bytes(event))
                    evdev_file.flush()'''
                    write_evdev(evdev_file, event_type, event_code, event_value)
                    

                except Exception as e:
                    print(f"Erreur lors du traitement de la trame : {e}")

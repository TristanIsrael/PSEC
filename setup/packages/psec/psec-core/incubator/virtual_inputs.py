from evdev import UInput, ecodes
import time
import struct
import socket
import msgpack

# Configuration du port série
SERIAL_PORT = "/var/run/sys-usb-input.sock"  # Remplacez par le port série réel
BAUDRATE = 9600

# Taille d'une trame packée (a=uint8, b=uint16, c=uint16, d=int32)
FRAME_FORMAT = "<BHHi"  # 'B': uint8, 'H': uint16, 'I': int32
FRAME_SIZE = struct.calcsize(FRAME_FORMAT)  # Taille attendue de la trame (9 octets)

# Configuration pour le périphérique uinput
capabilities = {
    ecodes.EV_KEY: [ecodes.BTN_LEFT, ecodes.BTN_RIGHT],  # Boutons de souris
    ecodes.EV_REL: [ecodes.REL_X, ecodes.REL_Y],        # Mouvements relatifs
}

# Créer un périphérique avec un nom unique
ui = UInput(capabilities, name="CustomMouseDevice")
print(f"Created uinput device: {ui.devnode}")

buffer = bytearray()
flush_interval = 0.1  # 100 millisecondes
last_flush_time = time.time()

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect(SERIAL_PORT)
#with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1) as ser:
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

            ui.write(event_type, event_code, event_value)                
            ui.syn()

        except Exception as e:
            print(f"Erreur lors du traitement de la trame : {e}")


ui.close()
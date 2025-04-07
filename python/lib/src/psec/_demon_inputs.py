import sys, glob, threading, serial, time, struct, msgpack
from typing import Optional
from evdev import InputDevice, ecodes, InputEvent
from . import Logger, Mouse, MouseButton, MouseWheel, MouseMove, Parametres, Cles, SingletonMeta
from . import MqttClient, Topics

class TypeEntree:
    INCONNU = 0
    CLAVIER = 1
    SOURIS = 2
    TOUCH = 3

INPUT_EVENT_FORMAT = "HHI"  # HH = type, code, I = value (unsigned int)
INPUT_EVENT_SIZE = struct.calcsize(INPUT_EVENT_FORMAT)

class DemonInputs(metaclass=SingletonMeta):
    """! Cette classe surveille les entrées des souris et clavier et transfère les informations au travers du XenBus 
    
    Le canal de communication *inputs* est utilisé pour transmettre les informations sur les périphériques d'entrée.

    Souris
    ------
    Les informations sur la souris sont transmises entièrement à chaque événement. Cela signifie que les informations 
    envoyées au travers du canal sont une représentation de la situation de la souris (position x et y, état de
    chaque bouton).
    
    """    

    mouse = Mouse()    
    chemin_socket_xenbus = None
    interface_xenbus_prete = False
    socket_xenbus = None
    monitored_inputs = []
    mouse_max_x = 1
    mouse_max_y = 1
    last_x = 0
    last_y = 0
    can_run = True


    def start(self, mqtt_client: MqttClient):
        self.mqtt_client = mqtt_client                
        #Logger().setup("Input daemon", mqtt_client)
        Logger().info("Starting input daemon", "Input daemon")
        self.can_run = True

        # On démarre la messagerie si elle ne l'est pas déjà
        self.chemin_socket_xenbus = Parametres().parametre(Cles.CHEMIN_SOCKET_INPUT_DOMU)
        if not self.__connecte_interface_xenbus():
            return

        # On connecte le listener pour la souris
        threading.Thread(target=self.__recherche_souris).start()
        threading.Thread(target=self.__recherche_tactile).start()
        #threading.Thread(target=self.__recherche_claviers).start()

    def stop(self):
        self.can_run = False
        self.__deconnecte_interface_xenbus()

    def __recherche_souris(self):
        # This function is ran in a specific thread
        Logger().info("Looking for a mouse...", "Input daemon")

        while True:
            inputs = glob.glob("/dev/input/event*")
            for input in inputs:
                #Logger().debug("Fichier {}".format(input))
                try:
                    dev = InputDevice(input)
                    type_input = self.__type_entree(dev)
                    if type_input == TypeEntree.SOURIS and input not in self.monitored_inputs:
                        threading.Thread(target= self.__surveille_souris, args=(dev,)).start()
                        self.monitored_inputs.append(input)
                except Exception:
                    pass # Ignore all errors silently
            
            # Wait a little and start over
            time.sleep(0.5)

    def __recherche_tactile(self):
        Logger().info("Looking for a touchscreen...", "Input daemon")

        while self.can_run:
            inputs = glob.glob("/dev/input/event*")

            for input in inputs:
                #Logger().debug("Fichier {}".format(input))
                
                try:          
                    dev = InputDevice(input)
                    type_input = self.__type_entree(dev)

                    if type_input == TypeEntree.TOUCH and input not in self.monitored_inputs:
                        # On récupère les valeurs max x et y pour connaître la résolution
                        caps = dev.capabilities()

                        # On filtre au cas où le périphérique n'aurait pas les capacités nécessaires
                        if not any(t[0] == ecodes.ABS_MT_POSITION_X for t in caps[ecodes.EV_ABS]):
                            continue

                        self.mouse_max_x = caps[ecodes.EV_ABS][ecodes.ABS_X][1].max
                        self.mouse_max_y = caps[ecodes.EV_ABS][ecodes.ABS_Y][1].max

                        #print("max_x={}, max_y={}".format(self.mouse.max_x, self.mouse.max_y))

                        threading.Thread(target= self.__surveille_tactile, args=(dev,)).start()
                        self.monitored_inputs.append(input)
                except:
                    pass # Ignore all errors silently

            # Wait a little and start over
            time.sleep(0.5)

    def __serialize_event(self, type_input, event):
        """Sérialise un événement pour transmission."""
        #data = [event.type, event.code, event.value]
        #payload = self.__packer.pack(data)
        #payload = struct.pack(INPUT_EVENT_FORMAT, event.type, event.code, event.value)
        # event.type : unsigned 16bit
        # event.code : unsigned 16bit
        # event.value : signed 32bit
        #payload = struct.pack('<BHHi', type_input, event.type, event.code, event.value)
        #print("Event : Type={}, Code={}, Value={}".format(ecodes.EV[event.type], ecodes.bytype[event.type][event.code], event.value))
        payload = msgpack.packb([type_input, event.type, event.code, event.value])
        return payload +b'\n'

    def __surveille_souris(self, input):
        Logger().info("Monitor the mouse {}".format(input.name), "Input daemon")

        try:
            for event in input.read_loop():  
                if event.type in [ecodes.EV_KEY, ecodes.EV_REL, ecodes.EV_ABS, ecodes.EV_SYN]:
                    serialized = self.__serialize_event(TypeEntree.SOURIS, event)
                    self.socket_xenbus.write(serialized)
                    #print(f"Sent: {serialized.strip()}")

                if not self.can_run:
                    return
        except:
            Logger().debug("The mouse {} is not available anymore".format(input.name), "Input daemon")
            self.monitored_inputs.remove(input.path)

    def __surveille_tactile(self, input):
        Logger().info("Monitor the touchscreen {}".format(input.name), "Input daemon")

        '''filtered_events = [
            ecodes.EV_KEY,
            ecodes.EV_MSC,
            ecodes.EV_ABS,
            ecodes.EV_SYN,
            ecodes.ABS_MT_SLOT,
            ecodes.ABS_MT_POSITION_X,
            ecodes.ABS_MT_POSITION_Y,
            ecodes.ABS_MT_TRACKING_ID
        ]'''

        try:
            for event in input.read_loop():
                #if event.type in filtered_events:
                serialized = self.__serialize_event(TypeEntree.TOUCH, event)
                self.socket_xenbus.write(serialized)
                #print(f"Sent: {serialized.strip()}")

                if not self.can_run:
                    return
        except:
            Logger().debug("The touchscreen {} is not available anymore".format(input.name), "Input daemon")
            self.monitored_inputs.remove(input.path)

    #def __recherche_claviers(self):
    #    Logger().info("Recherche d'un clavier")
    #    inputs = glob.glob("/dev/input/event*")
    #    for input in inputs:
    #        Logger().debug("Fichier {}".format(input))            
    #        dev = InputDevice(input)
    #        type_input = self.__type_entree(dev)
    #        if type_input == TypeEntree.CLAVIER:
    #            threading.Thread(target= self.__surveille_clavier, args=(dev,)).start()
    
    #def __surveille_clavier(self, input):
    #    Logger().info("Surveille le clavier {}".format(input.name))
    #
    #    for event in input.read_loop():
    #        if event.type == ecodes.EV_KEY and event.value == 0: # Key_UP
    #            self.__on_keypress(event.code)

    def __type_entree(self, entree : InputDevice):
        caps = entree.capabilities()
        keys = caps.get(ecodes.EV_KEY)

        if keys is None:
            return TypeEntree.INCONNU
        
        if ecodes.KEY_ESC in keys:
            return TypeEntree.CLAVIER
        elif ecodes.BTN_LEFT in keys:
            return TypeEntree.SOURIS
        elif ecodes.BTN_TOUCH in keys:
            return TypeEntree.TOUCH
    
    def __connecte_interface_xenbus(self) -> bool:
        #Ouvre le flux avec la socket
        Logger().debug("Open Xenbus I/O channel {}".format(self.chemin_socket_xenbus), "Input daemon")

        try:
            self.socket_xenbus = serial.Serial(port= self.chemin_socket_xenbus)
            self.interface_xenbus_prete = True            
            Logger().info("I/O channel is open", "Input daemon")
            return True          
        except serial.SerialException as e:
            self.socket_xenbus = None            
            Logger().error("Impossible to open the serial port {}".format(self.chemin_socket_xenbus), "Input daemon")
            Logger().error(str(e), "Input daemon")
            return False
        
    def __deconnecte_interface_xenbus(self):
        if self.socket_xenbus is not None:
            Logger().debug("Close Xenbus I/O socket", "Input daemon")
            self.socket_xenbus.close()
        
    '''def __envoie_evenement_souris(self, mouse: Optional[Mouse] = None):
        data = mouse.serialize() if mouse is not None else self.mouse.serialize()
        #Logger().debug(data)
        self.socket_xenbus.write(data +b'\n')
    '''
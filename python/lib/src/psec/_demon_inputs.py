import sys, glob, threading, serial, time
from typing import Optional
from evdev import InputDevice, ecodes
from . import Logger, Mouse, MouseButton, MouseWheel, MouseMove, Parametres, Cles, SingletonMeta
from . import MqttClient, Topics

class TypeEntree:
    INCONNU = 0
    CLAVIER = 1
    SOURIS = 2
    TOUCH = 3

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
    
    def __init__(self, client_msg: MqttClient, client_log: MqttClient):
        self.client_msg = client_msg
        Logger().setup("Input daemon", client_log)

    def start(self):
        Logger().info("Starting input daemon")
        
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

    def genere_evenement_souris(self, mouse:Mouse):
        #Logger().info("Envoi d'un événement de souris par l'API")
        self.__envoie_evenement_souris(mouse)

    ###
    # Fonctions privées
    #
    def __on_move(self, axe, delta: float):
        if delta == 0:
            return
        
        delta_x = 0 if axe != ecodes.REL_X else delta
        delta_y = 0 if axe != ecodes.REL_Y else delta

        #Logger().debug("Le mouvement du pointeur est {},{}".format(delta_x, delta_y))

        self.mouse.move = MouseMove.RELATIVE
        self.mouse.x = int(delta_x)
        self.mouse.y = int(delta_y)
        self.mouse.wheel = MouseWheel.NO_MOVE
        self.__envoie_evenement_souris()

    def __on_position(self, x:int, y:int, touched:int):
        #Logger().debug("Les coordonnées du pointeur sont {},{}".format(x, y))

        self.mouse.move = MouseMove.ABSOLUTE
        if touched > 0:
            self.mouse.buttons |= MouseButton.LEFT
        else:
            self.mouse.buttons &= ~MouseButton.LEFT

        self.mouse.x = int(x / self.mouse_max_x*100)
        self.mouse.y = int(y / self.mouse_max_y*100)
        self.mouse.wheel = MouseWheel.NO_MOVE
        
        if self.last_x != self.mouse.x or self.last_y != self.mouse.y or touched == 0:
            self.__envoie_evenement_souris()            
            self.last_x = self.mouse.x
            self.last_y = self.mouse.y        

    def __on_wheel(self, delta: int):
        if delta == 0:
            return 
        
        self.mouse.wheel = delta
        #Logger().debug("Actionnement de la molette : {}".format(self.mouse.wheel))                
        self.mouse.x = 0
        self.mouse.y = 0        
        self.__envoie_evenement_souris()

        # On réinitialise la molette
        self.mouse.wheel = MouseWheel.NO_MOVE

    def __on_click(self, bouton, etat):
        Logger().debug("L'état du bouton {} de la souris est {}".format(bouton, etat))
        self.mouse.x = 0
        self.mouse.y = 0

        if bouton == ecodes.BTN_LEFT:
            if etat > 0:
                self.mouse.buttons |= MouseButton.LEFT
            else:
                self.mouse.buttons &= ~MouseButton.LEFT
        elif bouton == ecodes.BTN_MIDDLE:
            if etat > 0:
                self.mouse.buttons |= MouseButton.MIDDLE
            else:
                self.mouse.buttons &= ~MouseButton.MIDDLE
        elif bouton == ecodes.BTN_RIGHT:
            if etat > 0:
                self.mouse.buttons |= MouseButton.RIGHT
            else:
                self.mouse.buttons &= ~MouseButton.RIGHT

        self.__envoie_evenement_souris()

    def __recherche_souris(self):
        # This function is ran in a specific thread
        Logger().info("Looking for a mouse...")

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
                except:
                    pass # Ignore all errors silently
            
            # Wait a little and start over
            time.sleep(0.5)

    def __recherche_tactile(self):
        Logger().info("Looking for a touchscreen...")

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
                        self.mouse_max_x = caps[ecodes.EV_ABS][ecodes.ABS_X][1].max
                        self.mouse_max_y = caps[ecodes.EV_ABS][ecodes.ABS_Y][1].max

                        #print("max_x={}, max_y={}".format(self.mouse.max_x, self.mouse.max_y))

                        threading.Thread(target= self.__surveille_tactile, args=(dev,)).start()
                        self.monitored_inputs.append(input)
                except:
                    pass # Ignore all errors silently

            # Wait a little and start over
            time.sleep(0.5)

    def __surveille_souris(self, input):
        Logger().info("Monitor the mouse {}".format(input.name))

        try:
            for event in input.read_loop():                
                if event.type == ecodes.EV_REL and (event.code == ecodes.REL_X or event.code == ecodes.REL_Y):
                    axe = event.code
                    delta = event.value
                    self.__on_move(axe, delta)
                elif event.type == ecodes.EV_REL and (event.code == ecodes.REL_WHEEL):
                    delta = event.value
                    self.__on_wheel(delta)
                elif event.type == ecodes.EV_KEY:
                    bouton = event.code
                    etat = event.value
                    self.__on_click(bouton, etat)

                if not self.can_run:
                    return
        except:
            Logger().debug("The mouse {} is not available anymore".format(input.name))
            self.monitored_inputs.remove(input.path)

    def __surveille_tactile(self, input):        
        Logger().info("Monitor the touchscreen {}".format(input.name))
        
        abs_x = -1
        abs_y = -1
        btn_touch = -1

        try:
            for event in input.read_loop():
                # Dans l'ordre, les événements reçus sont :
                # - BTN_TOUCH = 1
                # - ABS_X
                # - ABS_Y
                # - BTN_TOUCH = 0
                # 
                # La surface tactile a sa propre résolution. La position du point peut être calculée
                # grâce à une règle de 3 prenant en compte la valeur max de ABS_MT_POSITION_X ou ABS_MT_POSITION_Y
                # par l'application contrôleur ayant connaissance de la résolution de l'écran.
                # Cette valeur max doit être transmise avec les coordonnées du toucher.
                if event.type != ecodes.EV_ABS and event.type != ecodes.EV_KEY:
                    continue #ignoré               
                elif event.type == ecodes.EV_ABS and event.code == ecodes.ABS_MT_POSITION_X:
                    abs_x = event.value                    
                elif event.type == ecodes.EV_ABS and event.code == ecodes.ABS_MT_POSITION_Y:
                    abs_y = event.value                  
                elif event.type == ecodes.EV_ABS and event.code == ecodes.ABS_X: 
                    abs_x = event.value                    
                elif event.type == ecodes.EV_ABS and event.code == ecodes.ABS_Y:
                    abs_y = event.value
                elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
                    btn_touch = event.value
                           
                # On envoie la position absolue
                if abs_x > -1 and abs_y > -1 and btn_touch > -1:
                    self.__on_position(abs_x, abs_y, btn_touch)

                    if btn_touch == 0:
                        # Après le relâchement on réinitialise le contexte
                        abs_x = -1
                        abs_y = -1    
                        btn_touch = -1

                if not self.can_run:
                    return
        except:
            Logger().debug("The touchscreen {} is not available anymore".format(input.name))
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

        if keys == None:
            return TypeEntree.INCONNU
        
        if ecodes.KEY_ESC in keys:
            return TypeEntree.CLAVIER
        elif ecodes.BTN_LEFT in keys:
            return TypeEntree.SOURIS
        elif ecodes.BTN_TOUCH in keys:
            return TypeEntree.TOUCH
    
    def __connecte_interface_xenbus(self) -> bool:
        #Ouvre le flux avec la socket
        Logger().debug("Open Xenbus I/O channel {}".format(self.chemin_socket_xenbus))

        try:
            self.socket_xenbus = serial.Serial(port= self.chemin_socket_xenbus)
            self.interface_xenbus_prete = True            
            Logger().info("Xenbus I/O channel {} is open".format(Parametres().identifiant_domaine()))  
            return True          
        except serial.SerialException as e:
            self.socket_xenbus = None            
            Logger().error("Impossible to open the serial port {}".format(self.chemin_socket_xenbus))
            Logger().error(e)
            return False
        
    def __deconnecte_interface_xenbus(self):
        if self.socket_xenbus is not None:
            Logger().debug("Close Xenbus I/O socket")
            self.socket_xenbus.close()
        
    def __envoie_evenement_souris(self, mouse: Optional[Mouse] = None):
        data = mouse.serialize() if mouse is not None else self.mouse.serialize()
        #Logger().debug(data)
        self.socket_xenbus.write(data +b'\n')
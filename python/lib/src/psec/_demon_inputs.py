import sys, glob, threading, serial
from typing import Optional
from evdev import InputDevice, ecodes
from . import Journal, Mouse, MouseButton, MouseWheel, Parametres, Cles, SingletonMeta

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

    journal = Journal("Démon entrées")
    mouse = Mouse()    
    chemin_socket_xenbus = None
    interface_xenbus_prete = False
    socket_xenbus = None
    
    def demarre(self):
        self.journal.info("Démarrage du démon de surveillance des entrées")
        
        # On démarre la messagerie si elle ne l'est pas déjà
        self.chemin_socket_xenbus = Parametres().parametre(Cles.CHEMIN_SOCKET_INPUT_DOMU)
        if not self.__connecte_interface_xenbus():
            return

        # On connecte le listener pour la souris
        threading.Thread(target=self.__recherche_souris).start()
        threading.Thread(target=self.__recherche_tactile).start()
        #threading.Thread(target=self.__recherche_claviers).start()

    def genere_evenement_souris(self, mouse:Mouse):
        #self.journal.info("Envoi d'un événement de souris par l'API")
        self.__envoie_evenement_souris(mouse)

    ###
    # Fonctions privées
    #
    def __on_move(self, axe, delta: float):
        if delta == 0:
            return
        
        delta_x = 0 if axe != ecodes.REL_X else delta
        delta_y = 0 if axe != ecodes.REL_Y else delta

        #self.journal.debug("Le mouvement du pointeur est {},{}".format(delta_x, delta_y))

        self.mouse.x = int(delta_x)
        self.mouse.y = int(delta_y)
        self.mouse.wheel = MouseWheel.NO_MOVE
        self.__envoie_evenement_souris()

    def __on_wheel(self, delta: int):
        if delta == 0:
            return 
        
        self.mouse.wheel = delta
        #self.journal.debug("Actionnement de la molette : {}".format(self.mouse.wheel))                
        self.mouse.x = 0
        self.mouse.y = 0        
        self.__envoie_evenement_souris()

        # On réinitialise la molette
        self.mouse.wheel = MouseWheel.NO_MOVE

    def __on_click(self, bouton, etat):
        #self.journal.debug("L'état du bouton {} de la souris est {}".format(bouton, etat))
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
        self.journal.info("Recherche d'une souris")
        inputs = glob.glob("/dev/input/event*")
        for input in inputs:
            self.journal.debug("Fichier {}".format(input))            
            dev = InputDevice(input)
            type_input = self.__type_entree(dev)
            if type_input == TypeEntree.SOURIS:
                threading.Thread(target= self.__surveille_souris, args=(dev,)).start()

    def __recherche_tactile(self):
        self.journal.info("Recherche d'un écran tactile")
        inputs = glob.glob("/dev/input/event*")
        for input in inputs:
            self.journal.debug("Fichier {}".format(input))            
            dev = InputDevice(input)
            type_input = self.__type_entree(dev)
            if type_input == TypeEntree.TOUCH:
                # On récupère les valeurs max x et y pour connaître la résolution
                caps = dev.capabilities()
                self.mouse.max_x = caps[ecodes.EV_ABS][ecodes.ABS_X][1].max
                self.mouse.max_y = caps[ecodes.EV_ABS][ecodes.ABS_Y][1].max

                threading.Thread(target= self.__surveille_tactile, args=(dev,)).start()

    def __surveille_souris(self, input):
        self.journal.info("Surveille la souris {}".format(input.name))

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

    def __surveille_tactile(self, input):
        self.journal.info("Surveille l'écran tactile {}".format(input.name))

        last_abs_x = -1
        last_abs_y = -1
        abs_x = -1
        abs_y = -1
        touchBegan = False
        nbPos = 0        

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
                continue                
            elif event.type == ecodes.EV_ABS and event.code == ecodes.ABS_MT_POSITION_X: # ABS_MT_POSITION_X arrive avant le BTN_TOUCH
                abs_x = event.value                    
            elif event.type == ecodes.EV_ABS and event.code == ecodes.ABS_MT_POSITION_Y:
                abs_y = event.value                    
            elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
                if event.value == 1:
                    touchBegan = True             
                else:
                    #self.touchEnd.emit( QPoint(int(abs_x), int(abs_y)), QSize(int(max_x), int(max_y)) )
                    # On envoie un premier signal pour la position du toucher
                    diff_x = last_abs_x - abs_x
                    diff_y = last_abs_y - abs_y
                    if diff_x != 0:
                        self.__on_move(ecodes.REL_X, diff_x)
                    if diff_y != 0:
                        self.__on_move(ecodes.REL_Y, diff_y)

                    abs_x = -1
                    abs_y = -1
                    nbPos = 0                    
            
            # Si les positions x et y sont connues on peut envoyer un signal de début ou de mise
            # à jour du toucher
            if abs_x > -1 and abs_y > -1:
                if nbPos > 1:
                    if abs_x != last_abs_x or abs_y != last_abs_y:
                        self.touchUpdate.emit( QPoint(int(abs_x), int(abs_y)), QSize(int(max_x), int(max_y)) )
                        last_abs_x = abs_x
                        last_abs_y = abs_y
                elif touchBegan is True:
                    self.touchBegin.emit( QPoint(int(abs_x), int(abs_y)), QSize(int(max_x), int(max_y)) )  
                    touchBegan = False
                nbPos += 1   

    #def __recherche_claviers(self):
    #    self.journal.info("Recherche d'un clavier")
    #    inputs = glob.glob("/dev/input/event*")
    #    for input in inputs:
    #        self.journal.debug("Fichier {}".format(input))            
    #        dev = InputDevice(input)
    #        type_input = self.__type_entree(dev)
    #        if type_input == TypeEntree.CLAVIER:
    #            threading.Thread(target= self.__surveille_clavier, args=(dev,)).start()
    
    #def __surveille_clavier(self, input):
    #    self.journal.info("Surveille le clavier {}".format(input.name))
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
        self.journal.debug("Ouvre le flux avec le port série Xenbus %s" % self.chemin_socket_xenbus)

        try:
            self.socket_xenbus = serial.Serial(port= self.chemin_socket_xenbus)
            self.interface_xenbus_prete = True            
            self.journal.info("Le canal d'entrées du domaine {} est ouvert".format(Parametres().identifiant_domaine()))  
            return True          
        except serial.SerialException as e:
            self.socket_xenbus = None            
            self.journal.error("Impossible de se connecter au port série %s" % self.chemin_socket_xenbus)
            self.journal.error(e)
            return False
        
    def __envoie_evenement_souris(self, mouse: Optional[Mouse] = None):
        data = mouse.serialize() if mouse is not None else self.mouse.serialize()
        #self.journal.debug(data)
        self.socket_xenbus.write(data +b'\n')
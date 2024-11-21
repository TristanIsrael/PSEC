class MouseButton():
    UNKNOWN   = 0 # b0000
    LEFT      = 1 # b0001
    MIDDLE    = 2 # b0010
    RIGHT     = 4 # b0100

class MouseWheel():
    NO_MOVE = 0
    UP      = 1
    DOWN    = -1

class Mouse():
    buttons = MouseButton.UNKNOWN
    x = 0
    y = 0
    max_x = 0
    max_y = 0
    wheel = MouseWheel.NO_MOVE

    def __init__(self, x:int=0, y:int=0, buttons:int=0, wheel:int=0, max_x:int=0, max_y:int=0):
        self.x = x
        self.y = y
        self.buttons = buttons
        self.wheel = wheel
        self.max_x = max_x
        self.max_y = max_y

    def equals(self, other) -> bool:
        """ Returns true if the position and the buttons are the same """
        return (other.x == self.x 
            and other.y == self.y
            and other.buttons == self.buttons
            and other.wheel == self.wheel)

    def buttons_equal(self, other) -> bool:
        """ Returns true if the buttons are the same """
        return other.buttons == self.buttons
    
    def button_equals(self, other, button:int) -> bool:
        return (self.buttons & button) == (other.buttons & button)
    
    def button_pressed(self, button:int) -> bool:
        return (self.buttons & button) > 0   

    def wheel_equals(self, other) -> bool:
        return self.wheel == other.wheel

    def wheel_moved(self) -> bool:
        return self.wheel != MouseWheel.NO_MOVE 

    def serialize(self) -> bytes:
        if self.max_x == 0 and self.max_y == 0:
            return "{},{},{},{}".format(self.x, self.y, self.buttons, self.wheel).encode()
        else:
            # pour une valeur absolue (tactile), les valeurs max x et y sont transmises
            # pour permettre au contrôleur de calculer la position exacte en fonction
            # de la résolution de l'écran
            return "{}[{}],{}[{}],{},{}".format(self.x, self.max_x, self.y, self.max_y, self.buttons, self.wheel).encode()
    
    @staticmethod
    def fromData(data: bytes):  
        if data.count(b',') < 2:
            return None
        else:
            s = data.split(b',')
            if data.count(b'[') > 0:
                # C'est un tactile
                str_x = s[0]
                spl = str_x.split(b'[')
                x = int(spl[0])
                max_x = int(spl[1][:-1])

                str_y = s[1]
                spl = str_y.split(b'[')
                y = int(spl[0])
                max_y = int(spl[1][:-1])
                return Mouse(x, y, int(s[2]), int(s[3]), max_x, max_y)
            else:
                return Mouse(int(s[0]), int(s[1]), int(s[2]), int(s[3]))
        
            

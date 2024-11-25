class MouseButton():
    UNKNOWN   = 0 # b0000
    LEFT      = 1 # b0001
    MIDDLE    = 2 # b0010
    RIGHT     = 4 # b0100

class MouseWheel():
    NO_MOVE = 0
    UP      = 1
    DOWN    = -1

class MouseMove():
    RELATIVE = 0
    ABSOLUTE = 1

class Mouse():
    buttons = MouseButton.UNKNOWN
    x:int = 0
    y:int = 0
    move = MouseMove.RELATIVE
    wheel = MouseWheel.NO_MOVE

    def __init__(self, move:MouseMove=MouseMove.RELATIVE):
        self.move = move

    def __init__(self, move:MouseMove=MouseMove.RELATIVE, x:int=0, y:int=0, buttons:int=0, wheel:int=0):
        self.x = x
        self.y = y
        self.move = move
        self.buttons = buttons
        self.wheel = wheel

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
        return "{},{},{},{},{}".format(self.move, self.x, self.y, self.buttons, self.wheel).encode()
    
    @staticmethod
    def fromData(data: bytes):
        if data.count(b',') < 4:
            return None
        else:
            try:
                s = data.split(b',')                 
                return Mouse(int(s[0]), int(s[1]), int(s[2]), int(s[3]), int(s[4]))
                #return Mouse(int(s[0]), int(s[1]), int(s[2]), int(s[3]), int(s[4]))            
            except:
                return None

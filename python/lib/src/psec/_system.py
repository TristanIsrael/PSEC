from . import SingletonMeta
import subprocess

class System(metaclass=SingletonMeta):

    _DEFAULT_SCREEN_SIZE = "1100,750"
    width = -1
    height = -1
    rotation = -1

    def get_screen_width(self) -> int:
        if self.width > -1:
            return self.width
        
        screen_size = self._get_screen_size()

        if "," in screen_size:            
            rotation = self.get_screen_rotation()
            if rotation == 0 or rotation == 180:
                self.width = int(screen_size.split(',')[0])
            else: 
                self.width = int(screen_size.split(',')[1])

            return self.width
        
        return 1024
    
    def get_screen_height(self):
        if self.height > -1:
            return self.height
        
        screen_size = self._get_screen_size()

        if "," in screen_size:            
            rotation = self.get_screen_rotation()
            if rotation == 0 or rotation == 180:
                self.height = int(screen_size.split(',')[1])
            else: 
                self.height = int(screen_size.split(',')[0])

            return self.height
        
        return 768

    def get_screen_rotation(self) -> int:
        if self.rotation > -1:
            return self.rotation
        
        try:
            res = subprocess.run(["xenstore-read", "/local/domain/system/screen_rotation"], capture_output=True, text=True, check=False)
            if res.returncode == 0:
                return int(res.stdout)
        except Exception:
            return 0
        
        return 0

    def _get_screen_size(self) -> str:
        try:
            res = subprocess.run(["xenstore-read", "/local/domain/system/screen_size"], capture_output=True, text=True, check=False)
            if res.returncode == 0:
                return res.stdout
        except Exception:
            return self._DEFAULT_SCREEN_SIZE    
        
        return self._DEFAULT_SCREEN_SIZE
    

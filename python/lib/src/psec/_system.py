from . import SingletonMeta
import subprocess
import platform

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
    
    def get_system_uuid(self):
        system = platform.system().lower()
        
        if system == 'linux':
            try:
                with open('/sys/class/dmi/id/product_uuid', 'r') as f:
                    return f.read().strip()
            except FileNotFoundError:
                return None  # UUID non disponible sur cette machine Linux
        
        elif system == 'windows':
            try:
                output = subprocess.check_output('wmic csproduct get uuid', shell=True)
                lines = output.decode().split('\n')
                uuid = [line.strip() for line in lines if line.strip() and "UUID" not in line]
                return uuid[0] if uuid else None
            except subprocess.CalledProcessError:
                return None  # Erreur lors de l'exécution de wmic
        
        elif system == 'darwin':  # macOS
            try:
                output = subprocess.check_output('ioreg -rd1 -c IOPlatformExpertDevice', shell=True)
                for line in output.decode().split('\n'):
                    if 'IOPlatformUUID' in line:
                        return line.split('"')[-2]
                return None
            except subprocess.CalledProcessError:
                return None  # Erreur lors de l'exécution de ioreg
        
        else:
            return None  # Système non supporté

from . import Parametres, Cles, Constantes, Logger
from pathlib import Path
import os
import hashlib
import subprocess
import shutil


class FichierHelper():   

    @staticmethod
    def get_disks_list() -> list:
        """ Cette fonction retourne la liste des disques externes rattachés au système 
        
            La liste des disques est obtenue à partie des dossiers contenus dans Constantes.CHEMIN_MONTAGE_USB 
            en vérifiant s'il s'agit d'un point de montage.
        """

        disques = []
        point_montage = Parametres().parametre(Cles.CHEMIN_MONTAGE_USB)
        #print("Recherche de disques USB dans {}".format(point_montage))                
        with os.scandir(point_montage) as dossiers:
            for dossier in dossiers:
                if dossier.is_dir():
                    if True: #os.path.ismount(dossier.path):
                        #print("Disque trouvé : {}".format(dossier.name))
                        disques.append(dossier.name)

        return disques

    @staticmethod
    def get_files_list(disk:str, recursive:bool, from_dir:str="") -> list:
        """ Cette fonction renvoie l'arborescence complète d'un point de montage
        
            Le chemin utilisé est constitué par la concaténation du paramètre CHEMIN_MONTAGE_USB et 
            du nom passé en paramètre

            Pour chaque fichier ou dossier, un dictionnaire est créé :
            { "type": "folder", "path": "/", "name": "dossier 1" },
            { "type": "file", "path": "/dossier 1", "name": "fichier 1", "size": 333344 },
            { "type": "file", "path": "/dossier 1/dossier 2", "name": "fichier 4", "size": 12 }
        """

        chemin:str = ""
        if disk == Constantes.REPOSITORY:
            chemin = Parametres().parametre(Cles.CHEMIN_DEPOT_DOM0)
        else:
            chemin_montage = Parametres().parametre(Cles.CHEMIN_MONTAGE_USB)
            if chemin_montage is None:
                print("No mount point defined. Aborting.")
                return []
            
            chemin = f"{chemin_montage}/{disk}"

        print(f"Getting files list for mount point {chemin}")
        fichiers = []
        FichierHelper.get_folder_contents(chemin, fichiers, len(chemin), recursive, from_dir)
        return fichiers
       
    @staticmethod
    def get_folder_contents(chemin:str, liste:list, decoupage:int = 0, recursif:bool = False, from_dir:str = ""):
        _real_filepath = "{}{}".format(chemin, from_dir)

        #print("get_folder_contents : {} ({})".format(from_dir, _real_filepath))
        with os.scandir(_real_filepath) as entrees:
            for entree in entrees:
                if entree.is_symlink():
                    continue
                
                filepath = "{}{}".format(chemin[decoupage:], from_dir)
                filename = entree.name
                if entree.is_file():
                    entryDict = {
                        "type": "file",
                        "path": "/" if filepath == "" else filepath,
                        "name": filename,
                        "size": entree.stat().st_size
                    }

                    liste.append(entryDict)
                elif entree.is_dir():
                    entryDict = {
                        "type": "folder",
                        "path": "/" if filepath == "" else filepath,
                        "name": filename
                    }

                    liste.append(entryDict)

                    if recursif:
                        FichierHelper.get_folder_contents(entree.path, liste, decoupage, recursif)


    @staticmethod
    def split_filepath(file_path:str) -> tuple[str, str]:
        spl = str.split(":")

        if len(spl) == 1:
            return ("", spl[0])
        else:
            return (spl[0], spl[1])

    @staticmethod
    def make_filepath(disk_name:str, file_name:str) -> str:
        return "{}:{}".format("" if disk_name == None else disk_name, file_name)

    @staticmethod
    def calculate_fingerprint(filepath:str) -> str:
        try:
            with open(filepath, "rb") as f:
                h = hashlib.file_digest(f, Constantes.FINGERPRINT_METHOD)
                return h.hexdigest()
        except Exception as e:
            print(f"An error occured while calculating the fingerprint of the file {filepath}")
            print(e)

        return ""
        
    @staticmethod
    def copy_file(source_location:str, filepath:str, destination_folder:str, source_fingerprint:str) -> str:
        ''' Copie le fichier source_filepath dans le répertoire destination_folder

        Le répertoire de destination doit exister.

        L'empreinte du fichier source est comparée avec celle de la copie.

        La fonction renvoie vrai si la copie s'est bien déroulée et que les empreintes coincident.
        '''
        
        cmd = ['cp', f"{source_location}{filepath}", f"{destination_folder}{filepath}"]
        #cmd = ['rsync', '-a', f"{source_location}{filepath}", f"{destination_folder}{filepath}"]
        #print(f"Run command {cmd}")
        
        try:
            subprocess.run(cmd, check= True, shell= False)
            #shutil.copy2(f"{source_location}{filepath}", f"{destination_folder}{filepath}")
        except subprocess.CalledProcessError as e:
            Logger().debug(f"The file {filepath} could not be copied to {destination_folder}. Error: {e}")
            return ""

        # Calculate the new file's fingerprint
        destination_file = f"{destination_folder}{filepath}"
        dest_fingerprint = FichierHelper.calculate_fingerprint(destination_file)

        if source_fingerprint == dest_fingerprint:
            return dest_fingerprint
        else:
            Logger().debug(f"The file {filepath} has been copied to {destination_folder} but the fingerprints differ")
            return ""


    @staticmethod
    def copy_file_to_repository(source_location:str, filepath:str, fingerprint:str):
        repository_path = str(Parametres().parametre(Cles.STORAGE_PATH_DOMU))
        FichierHelper.copy_file(source_location, filepath, repository_path, fingerprint)

    @staticmethod
    def create_file(filepath:str, size_ko:int):
        with open(filepath, 'wb') as fout:
            fout.write(os.urandom(size_ko*1024))

    @staticmethod
    def remove_file(filepath:str) -> bool:
        try:
            os.remove(filepath)
            return True
        except Exception:
            return False
        
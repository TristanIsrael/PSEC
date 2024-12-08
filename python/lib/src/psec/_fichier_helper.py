from . import Parametres, Cles, Constantes, Logger
from pathlib import Path
import os, hashlib, subprocess

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
            if chemin_montage == None:
                print("Aucun point de montage défini. Abandon")
                return []
            
            chemin = "{}/{}".format(chemin_montage, disk)

        print("Récupération de la liste des fichiers pour le point de montage {}".format(chemin))
        fichiers = []
        FichierHelper.get_folder_contents(chemin, fichiers, len(chemin), recursive, from_dir)
        return fichiers
       
    @staticmethod
    def get_folder_contents(chemin:str, liste:list, decoupage:int = 0, recursif:bool = False, from_dir:str = ""):
        with os.scandir("{}{}".format(chemin, from_dir)) as entrees:
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
    def calculate_footprint(filepath:str) -> str:
        try:
            with open(filepath, "rb") as f:            
                hash = hashlib.file_digest(f, Constantes.FOOTPRINT_METHOD)
                return hash.hexdigest()                
        except Exception as e:
            print("Erreur")
            print(e)

        return ""
        
    @staticmethod
    def copy_file(source_location:str, filepath:str, destination_folder:str, source_footprint:str) -> str:
        ''' Copie le fichier source_filepath dans le répertoire destination_folder

        Le répertoire de destination doit exister.

        L'empreinte du fichier source est comparée avec celle de la copie.

        La fonction renvoie vrai si la copie s'est bien déroulée et que les empreintes coincident.
        '''
        
        cmd = ['cp', "{}/{}".format(source_location, filepath), destination_folder]
        print("Exécution de la commande {}".format(cmd))
        
        proc = subprocess.run(cmd, check= True, shell= False)        
        if proc.returncode != 0:
            Logger().debug("The file {} could not be copied to {}. Error: {}".format(filepath, destination_folder, proc.stderr))
            return ""
        else:
            # Calculate the new file's footprint
            destination_file = "{}{}".format(destination_folder, filepath)
            dest_footprint = FichierHelper.calculate_footprint(destination_file)

            if source_footprint == dest_footprint:
                return dest_footprint
            else:
                Logger().debug("The file {} has been copied to {} but the footprints differ".format(filepath, destination_folder))
                return ""

    @staticmethod
    def copy_file_to_repository(source_location:str, filepath:str, footprint:str):
        repository_path = str(Parametres().parametre(Cles.STORAGE_PATH_DOMU))
        FichierHelper.copy_file(source_location, filepath, repository_path, footprint)

    @staticmethod
    def create_file(filepath:str, size_ko:int):
        with open(filepath, 'wb') as fout:
            fout.write(os.urandom(size_ko*1024))
                        
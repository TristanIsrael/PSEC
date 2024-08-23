from . import Parametres, Cles, Constantes
import os, hashlib, subprocess

class FichierHelper():   

    @staticmethod
    def get_liste_disques() -> list:
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
    def get_liste_fichiers(nom_disque) -> list:
        """ Cette fonction renvoie l'arborescence complète d'un point de montage
        
            Le chemin utilisé est constitué par la concaténation du paramètre CHEMIN_MONTAGE_USB et 
            du nom passé en paramètre

            Pour chaque fichier ou dossier, un dictionnaire est créé :
            { "type": "folder", "path": "/", "name": "dossier 1" },
            { "type": "file", "path": "/dossier 1", "name": "fichier 1", "size": 333344 },
            { "type": "file", "path": "/dossier 1/dossier 2", "name": "fichier 4", "size": 12 }
        """

        chemin:str = ""
        if nom_disque == Constantes.REPOSITORY:
            chemin = Parametres().parametre(Cles.CHEMIN_DEPOT_DOM0)
        else:
            chemin_montage = Parametres().parametre(Cles.CHEMIN_MONTAGE_USB)
            if chemin_montage == None:
                print("Aucun point de montage défini. Abandon")
                return []
            
            chemin = "{}/{}".format(chemin_montage, nom_disque)

        print("Récupération de la liste des fichiers pour le point de montage {}".format(chemin))
        fichiers = []
        FichierHelper.__get_contenu_dossier(chemin, fichiers, len(chemin))
        return fichiers
       
    @staticmethod
    def __get_contenu_dossier(chemin, liste, decoupage = 0):
        with os.scandir(chemin) as entrees:
            for entree in entrees:
                filepath = chemin[decoupage:]
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
                    FichierHelper.__get_contenu_dossier(entree.path, liste, decoupage)

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
        with open(filepath, "rb") as f:            
            hash = hashlib.file_digest(f, Constantes.FOOTPRINT_METHOD)
            return hash.hexdigest()                
        
    @staticmethod
    def copy_file(source_filepath:str, destination_folder:str, footprint:str):
        ''' Copie le fichier source_filepath dans le répertoire destination_folder

        L'empreinte du fichier source est comparée avec celle de la copie.

        La fonction renvoie vrai si la copie s'est bien déroulée et que les empreintes coincident.
        '''
        
        cmd = ['cp', source_filepath, destination_folder]
        print("Exécution de la commande {}".format(cmd))
        
        subprocess.run(cmd, check= True, shell= False)        

    @staticmethod
    def copy_file_to_repository(source_filepath:str, footprint:str):
        repository_path = str(Parametres().parametre(Cles.CHEMIN_DEPOT_DOMU))
        FichierHelper.copy_file(source_filepath, repository_path, footprint)

    @staticmethod
    def create_file(filepath:str, size_ko:int):
        with open(filepath, 'wb') as fout:
            fout.write(os.urandom(size_ko*1024))
                        
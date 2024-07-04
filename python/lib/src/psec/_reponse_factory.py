from . import Reponse, TypeReponse, Constantes, Domaine, Parametres, Cles

class ReponseFactory():
    """ La classe ReponseFactory permet de générer les messages en réponse à certaines commandes.    
    
    """

    @staticmethod
    def cree_reponse_liste_disques(liste_disques:list = list(), destination:str = Domaine.TOUS):
        reponse = Reponse(TypeReponse.LISTE_DISQUES, liste_disques)
        ReponseFactory._ajoute_source(reponse)
        reponse.destination = destination
        return reponse
    
    @staticmethod
    def cree_reponse_liste_fichiers(nom_disque:str, liste_fichiers:list = list(), destination:str = Domaine.TOUS):
        data = {
            "disk": nom_disque,
            "files": liste_fichiers
        }
        reponse = Reponse( TypeReponse.LISTE_FICHIERS, data )
        ReponseFactory._ajoute_source(reponse)
        reponse.destination = destination
        return reponse

    @staticmethod
    def cree_reponse_benchmark_inputs(duree:int, iterations:int, emetteur:str):
        data = {
            "duration": duree,
            "iterations": iterations
        }
        reponse = Reponse( TypeReponse.BENCHMARK_INPUTS, data )
        ReponseFactory._ajoute_source(reponse)
        reponse.destination = emetteur
        return reponse

    @staticmethod
    def cree_reponse_benchmark_fichiers_demarre(emetteur:str):
        data = {
            "etat": "demarre"
        }
        reponse = Reponse( TypeReponse.BENCHMARK_FILES, data )
        ReponseFactory._ajoute_source(reponse)
        reponse.destination = emetteur
        return reponse
    
    @staticmethod
    def cree_reponse_benchmark_fichiers_termine(emetteur:str, metrics:list):
        data = {
            "etat": "termine",
            "metrics": metrics
        }
        reponse = Reponse( TypeReponse.BENCHMARK_FILES, data )
        ReponseFactory._ajoute_source(reponse)
        reponse.destination = emetteur
        return reponse

    @staticmethod
    def cree_reponse_benchmark_fichiers_erreur(erreur:str, emetteur:str):
        data = {
            "etat": "erreur",
            "message": erreur
        }
        reponse = Reponse( TypeReponse.BENCHMARK_FILES, data )
        ReponseFactory._ajoute_source(reponse)
        reponse.destination = emetteur
        return reponse
    
    @staticmethod
    def cree_reponse_file_footprint(filepath:str, disk:str, footprint:str):
        data = {
            "filepath": filepath,
            "disk": disk,
            "footprint": footprint
        }
        reponse = Reponse( TypeReponse.FILE_FOOTPRINT, data)
        ReponseFactory._ajoute_source(reponse)
        return reponse
    
    @staticmethod
    def cree_reponse_create_file(filepath:str, disk:str, footprint:str, success:bool):
        data = {
            "filepath": filepath,
            "disk": disk,
            "footprint": footprint,
            "success": success
        }
        reponse = Reponse( TypeReponse.FILE_CREATION, data)
        ReponseFactory._ajoute_source(reponse)
        return reponse
       
    @staticmethod
    def _ajoute_source(reponse):
        reponse.source = Parametres().parametre(Cles.IDENTIFIANT_DOMAINE)
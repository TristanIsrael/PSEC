from . import EtatComposant, BenchmarkId

class ResponseFactory():
    """ La classe ResponseFactory permet de générer les messages en réponse à certaines commandes.    
    
    """

    @staticmethod
    def create_response_disks_list(disks_list:list = list()) -> dict:
        payload = {
            "disks": disks_list
        }        
        return payload
    
    @staticmethod
    def create_response_list_files(disk:str, files:list = list()) -> dict:
        payload = {
            "disk": disk,
            "files": files
        }        
        return payload

    @staticmethod
    def cree_reponse_benchmark_inputs(duree:int, iterations:int) -> dict:
        payload = {
            "id": BenchmarkId.INPUTS,
            "duration": duree,
            "iterations": iterations
        }
        return payload

    @staticmethod
    def cree_reponse_benchmark_fichiers_demarre() -> dict:
        payload = {
            "id": BenchmarkId.FILES,
            "state": "started"
        }
        return payload
    
    @staticmethod
    def cree_reponse_benchmark_fichiers_termine(metrics:list) -> dict:
        payload = {
            "id": BenchmarkId.FILES,
            "estatetat": "finished",
            "metrics": metrics
        }
        return payload

    @staticmethod
    def cree_reponse_benchmark_fichiers_erreur(erreur:str) -> dict:
        payload = {
            "id": BenchmarkId.FILES,
            "state": "error",
            "message": erreur
        }
        return payload
    
    @staticmethod
    def create_response_file_footprint(filepath:str, disk:str, footprint:str) -> dict:
        payload = {
            "filepath": filepath,
            "disk": disk,
            "footprint": footprint
        }
        return payload
    
    @staticmethod
    def create_response_create_file(filepath:str, disk:str, footprint:str, success:bool) -> dict:
        payload = {
            "filepath": filepath,
            "disk": disk,
            "footprint": footprint,
            "success": success
        }
        return payload

    @staticmethod
    def cree_reponse_etat_composant(nom:str, etat:EtatComposant) -> dict:
        payload = {
            "composant": nom,
            "etat": etat
        }
        return payload

    @staticmethod
    def create_response_copy_file(filepath:str, disk:str, success:bool, footprint:str) -> dict:
        payload = {
            "filepath": filepath,
            "status": "ok" if success else "error",
            "footprint": footprint
        }
        return payload
    
    
    @staticmethod
    def create_response_shutdown(accepted:bool):
        payload = {
            "state": "accepted" if accepted else "refused",
            "reason": ""
        }

        return payload
    

    @staticmethod
    def create_response_restart_domain(domain_name:str, accepted:bool):
        payload = {
            "domain_name": domain_name,
            "state": "accepted" if accepted else "refused",
            "reason": ""
        }

        return payload
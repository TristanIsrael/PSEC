from . import EtatComposant

class ComponentsHelper():

    components_ = []

    def __init__(self):
        components_ = []

    def update(self, updates:list) -> None:
        components_dict = {comp["id"]: comp for comp in self.components_}
    
        for update in updates:
            if update["id"] in components_dict:
                # Si l'id existe, mettre à jour uniquement le champ 'state'
                components_dict[update["id"]]["state"] = update["state"]
            else:
                # Si l'id n'existe pas, ajouter l'entrée
                self.components_.append(update)

    def get_by_id(self, id:str) -> dict:
        for comp in self.components_:
            if comp.get("id") is not None and comp.get("id") == id:
                return comp
        return {}

    def get_ids(self) -> list[str]:
        return [d["id"] for d in self.components_ if "id" in d]
    
    def get_states(self) -> dict:
        return {comp["id"]: comp["state"] for comp in self.components_ if "id" in comp and "state" in comp}
    
    def get_state(self, id:str):
        for comp in self.components_:
            if comp.get("id") == id:
                return comp.get("state", EtatComposant.UNKNOWN)
            
        return EtatComposant.UNKNOWN
    
    def get_type(self, id:str) -> str:
        for comp in self.components_:
            if comp.get("id") == id:
                return comp.get("type", "")
            
        return ""
    
    def get_ids_by_type(self, type:str) -> list[str]:
        ids = list()

        for comp in self.components_:
            if comp.get("type") is not None and comp.get("type") == type:
                ids.append(comp.get("id", ""))
            
        return ids
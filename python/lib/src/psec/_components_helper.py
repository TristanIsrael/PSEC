from . import EtatComposant

class ComponentsHelper():

    def __init__(self):
        self.__components = []

    def update(self, updates:list) -> None:
        components_dict = {comp["id"]: comp for comp in self.__components}
    
        for update in updates:
            if update["id"] in components_dict:
                # Si l'id existe, mettre à jour uniquement le champ 'state'
                components_dict[update["id"]]["state"] = update.get("state", EtatComposant.UNKNOWN)
            else:
                # Si l'id n'existe pas, ajouter l'entrée
                self.__components.append(update)

    def get_by_id(self, id:str) -> dict:
        for comp in self.__components:
            if comp.get("id") is not None and comp.get("id") == id:
                return comp
            
        return {}

    def get_ids(self) -> list[str]:
        return [d["id"] for d in self.__components if "id" in d]
    
    def get_states(self) -> dict:
        return {comp["id"]: comp["state"] for comp in self.__components if "id" in comp and "state" in comp}
    
    def get_state(self, id:str):
        for comp in self.__components:
            if comp.get("id") == id:
                return comp.get("state", EtatComposant.UNKNOWN)
            
        return EtatComposant.UNKNOWN
    
    def get_type(self, id:str) -> str:
        for comp in self.__components:
            if comp.get("id") == id:
                return comp.get("type", "")
            
        return ""
    
    def get_ids_by_type(self, type:str) -> list[str]:
        ids = list()

        for comp in self.__components:
            if comp.get("type") is not None and comp.get("type") == type:
                ids.append(comp.get("id", ""))
            
        return ids
    
    def get_components(self):
        return self.__components
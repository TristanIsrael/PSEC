from . import Constantes, Parametres, Cles, Domaine
import time, json, zlib

class TypeMessage:
    INDEFINI = "indefini"
    NOTIFICATION = "notification"
    COMMANDE = "commande"
    REPONSE = "reponse"

class Message:
    """Cette classe encapsule les données d'un message
    
    Un message transporte plusieurs types d'informations : notification, commande, réponse.
    """

    id = 0
    type:str = TypeMessage.INDEFINI
    source:str = Domaine.INDEFINI
    destination:str = Domaine.INDEFINI
    payload = {}
    compact = True # Pour le débogage il peut être utile de passer cette valeur à False      
    logger = None      

    def __init__(self, type = TypeMessage.INDEFINI, destination = Domaine.INDEFINI, payload = {}):        
        self.identifiant = time.time_ns()
        self.type = type
        self.source = Parametres().parametre(Cles.IDENTIFIANT_DOMAINE)
        self.destination = destination
        self.payload = payload

    @staticmethod
    def from_json(json):
        # Vérification du formatage du message
        if "type" in json and "source" in json and "destination" in json and "payload" in json:
            msg = Message(json["type"], json["destination"], json["payload"])
            msg.source = json["source"]
            return msg
        else:
            print("Erreur : le message est mal formaté (au moins un champ manquant)")
            return None

    def to_json(self):
        j = {
            "type": self.type,
            "source": self.source,
            "destination": self.destination,
            "payload": self.payload
        }

        strjson = ""

        if self.compact:
            strjson = "{}".format(json.dumps(j, separators=(',', ':')))
        else:
            strjson = "{}".format(json.dumps(j, sort_keys=True, indent=4))
        
        return strjson.encode()

    def print(self):
        print(self.to_json())
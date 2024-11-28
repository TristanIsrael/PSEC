from ._message import Message, TypeMessage
from ._commande import TypeCommande

class Reponse(Message):
    """Classe définissant une réponse asynchrone à l'exécution d'une commande sur un domaine"""

    commande = TypeCommande.INDEFINIE
    data = ""

    def __init__(self, commande, data):
        super().__init__()
        self.type = TypeMessage.REPONSE
        self.commande = commande
        self.data = data

        self.__update_payload()

    def __update_payload(self):
        self.payload = {
            "commande": self.commande,
            "data": self.data
        }
from ._message import Message, TypeMessage
from ._type_commande import TypeCommande

class Commande(Message):
    """Classe définissant une commande à exécuter sur un domaine"""
    
    commande : TypeCommande = TypeCommande.INDEFINIE
    arguments : str = ""    

    def __init__(self, commande, arguments):
        super().__init__()
        self.type = TypeMessage.COMMANDE
        self.commande = commande
        self.arguments = arguments

        self.__update_payload()

    def __update_payload(self):
        self.payload = {
            "commande": self.commande,
            "arguments": self.arguments
        }

from . import TypeMessage, Message, TypeEvenement

class Notification(Message):
    """ Classe définissant une notification """

    evenement = ""
    data = ""

    def __init__(self, evenement:str, data):
        super().__init__()
        self.type = TypeMessage.NOTIFICATION
        self.evenement = evenement
        self.data = data

        self.__update_payload()

    def __update_payload(self):
        self.payload = {
            "evenement": self.evenement,
            "data": self.data
        }

#class NotificationInput(Notification):
#    """ Cette classe permet de définir une notification concernant une IHM """
#
#    type = TypeEntree.INDEFINI
#
#    def __init__(self, type : TypeEntree):
#        super().__init__(TypeEvenement.ENTREE, {})
#        self.type = type
from . import Journal, Notification, TypeEvenement, MessagerieDomu

class Debug():
    """ Cette classe sert à débugger le système """

    journal = None

    def __init__(self):
        self.journal = Journal("Debug")
        self.journal.debug("Instanciation du débogeur")        

    def emet_notification_test(self):
        notif = Notification(TypeEvenement.DISQUE, { "message": "Ceci est une notification de test" })
        MessagerieDomu().envoie_message_xenbus(notif)
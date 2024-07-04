import json, zlib
from . import Notification, TypeMessage, Commande, Message, Reponse

class MessageHelper():

    @staticmethod
    def decode_json(data):
        try:
            obj = json.loads(data)
            return obj
        except json.JSONDecodeError:
            print("ERREUR lors du décodage de la trame JSON %s" % data)

    @staticmethod
    def cree_message_from_json(data : bytes) -> Message:
        decoded = MessageHelper.decode_json(data.decode())

        if decoded == None:
            print("ERREUR de décodage JSON")
            return None # Erreur silencieuse ?

        if decoded.get("type") == TypeMessage.NOTIFICATION:
            payload = decoded.get("payload")
            if payload != None:
                notif = Notification(payload.get("evenement"), payload.get("data"))
                notif.source = decoded.get("source")
                notif.destination = decoded.get("destination")
                return notif
        elif decoded.get("type") == TypeMessage.COMMANDE:
            payload = decoded.get("payload")
            if payload != None:
                cmd = Commande(payload.get("commande"), payload.get("arguments"))
                cmd.source = decoded.get("source")
                cmd.destination = decoded.get("destination")
                return cmd
        elif decoded.get("type") == TypeMessage.REPONSE:
            payload = decoded.get("payload")
            if payload != None:
                rep = Reponse(payload.get("commande"), payload.get("data"))
                rep.source = decoded.get("source")
                rep.destination = decoded.get("destination")
                return rep
from . import Constantes, EtatDisque, EtatFichier, Domaine, BoutonSouris
from . import TypeEntree, Parametres, TypeEvenement, Notification, TypeMessage, Cles

class NotificationFactory:
    """ Cette classe permet de créer des notifications simmplement.

    Les fonctions de cette classes sont statiques.
    """

    @staticmethod
    def __nom_domaine_gui() -> str:
        nom = str(Parametres().parametre(Cles.NOM_DOMAINE_GUI))
        return nom

    @staticmethod
    def cree_notification_domu_pret(destination:str = Domaine.DOM0):
        notif = Notification(TypeEvenement.ETAT_DOMU, {"pret": 1})
        notif.destination = destination
        return notif

    @staticmethod
    def cree_notification_domu_nonpret(destination:str = Domaine.DOM0):
        notif = Notification(TypeEvenement.ETAT_DOMU, {"pret": 0})
        notif.destination = destination
        return notif
    
    @staticmethod
    def cree_notification_disque(nom:str, etat:str, destination:str = Domaine.TOUS):
        notif = Notification(
            TypeEvenement.DISQUE, 
            {
                "nom": nom, 
                "etat": etat
            }
        )
        notif.destination = destination
        return notif
    
    @staticmethod
    def cree_notification_fichier(nom : str, etat:str, destination:str = Domaine.TOUS):
        notif = Notification(
            TypeEvenement.FICHIER, 
            {
                "fichier": nom, 
                "etat": etat
            }
        )
        notif.destination = destination
        return notif

    @staticmethod
    def cree_notification_souris(position_x : int, position_y : int, bouton : BoutonSouris = BoutonSouris.AUCUN):
        """ Cette fonction permet de créer une notification concernant la souris """   
    
        data = {
            "entree": TypeEntree.SOURIS,
            "position": {
                "x": position_x,
                "y": position_y
            },
            "boutons" : {
                "gauche": 1 if bouton == BoutonSouris.GAUCHE else 0,
                "milieu": 1 if bouton == BoutonSouris.MILIEU else 0,
                "droit": 1 if bouton == BoutonSouris.DROIT else 0
            }
        }

        notif = Notification(TypeEvenement.ENTREE, data)
        notif.source = Parametres().identifiant_domaine()
        notif.destination = NotificationFactory.__nom_domaine_gui()
        return notif
    
    @staticmethod
    def cree_notification_tactile(position_x : int, position_y : int, touche : bool):
        data = {
            "entree": TypeEntree.TACTILE,
            "position": {
                "x": position_x,
                "y": position_y
            },
            "touche": 1 if touche else 0
        }

        notif = Notification(TypeEvenement.ENTREE, data)
        notif.source = Parametres().identifiant_domaine()
        notif.destination = NotificationFactory.__nom_domaine_gui()
        return notif
    
    @staticmethod
    def cree_notification_clavier(touche):
        """ Cette fonction permet de définir une notification concernant une frappe clavier """

        data = {
            "entree": TypeEntree.CLAVIER,
            "touche": touche
        }
        
        notif = Notification(TypeEvenement.ENTREE, data)
        notif.source = Parametres().identifiant_domaine()
        notif.destination = NotificationFactory.__nom_domaine_gui()
        return notif

    @staticmethod
    def cree_notification_test(donnees : dict):
        notif = Notification(TypeEvenement.TEST, donnees)
        notif.source = Parametres().identifiant_domaine()
        notif.destination = Domaine.TOUS
        return notif
    
    @staticmethod
    def cree_notification_nouveau_fichier(filepath:str, disk:str, footprint:str):
        data = {
            "filepath": filepath,
            "disk": disk,
            "original_footprint": footprint
        }

        notif = Notification(TypeEvenement.FICHIER, data)
        notif.source = Parametres().identifiant_domaine()
        notif.destination = Domaine.TOUS
        return notif
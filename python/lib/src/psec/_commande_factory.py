from . import Commande, TypeCommande, Constantes, Domaine, Parametres, Cles

class CommandeFactory():
    ''' La classe MessageFactory permet de générer les notification, commandes et
    erreurs utilisées dans le cadre des échanges entre domaines.

    L'émetteur de la commande est automatiquement ajouté lors de sa création.

    Pour rappel les domaines impliqués dans le socle sont :
    - sys-usb qui gère les accès aux supports USB

    Les notification sont les suivantes :
    - Le DomU informe le Dom0 qu'il a démarré (DomU -> Dom0)
    - La sys-usb informe le Dom0 qu'un support USB a été connecté (DomU -> Dom0)
    - La sys-usb informe le Dom0 qu'un support USB a été déconnecté (DomU -> Dom0)

    Les commandes sont les suivantes :
    - Journalisation
      - Un domaine ajoute une entrée dans le journal (Dom* -> Dom0)
      - Le Dom0 enregistre le journal sur le support USB de sortie (DomU -> Dom0)
    - Système
      - Le DomU demande l'état d'activation du débogage (DomU -> Dom0)
      - Le DomU demande le redémarrage du système (DomU -> Dom0)
      - Le DomU demande l'arrêt du système (DomU -> Dom0)
      - Le DomU demande la réinitialisation d'un autre DomU (DomU -> Dom0)
      - Le DomU demande le niveau de charge de la batterie (DomU -> Dom0)
      - Le DomU demande l'état de l'alimentation secteur (DomU -> Dom0)
    - Fichiers
      - Le DomU demande la liste des fichiers d'un support USB (DomU -> Dom0 ; Dom0 -> sys-usb)
      - Le DomU demande la création d'une archive sécurisée sur le support USB de sortie (DomU -> Dom0 ; Dom0 -> sys-usb)
      - Le DomU demande l'ajout d'un fichier à l'archive sécurisée sur le support USB de sortie (DomU -> Dom0 ; Dom0 -> sys-usb)
      - Le DomU demande la copie d'un fichier (DomU -> Dom0 ; Dom0 -> sys-usb)      
    - Notifications
      - Le DomU notifie l'appui sur une touche de clavier (DomU -> Dom0 -> *)
      - Le DomU notifie l'appui sur un bouton de souris (DomU -> Dom0 -> *)
      - Le DomU notifie le déplacement de la souris (DomU -> Dom0 -> *)
      - Le DomU informe le toucher de l'écran tactile (DomU -> Dom0 -> *)
    
    '''    

    @staticmethod
    def cree_commande_liste_disques():
        commande = Commande(TypeCommande.LISTE_DISQUES, {} )
        CommandeFactory.__ajoute_source(commande)
        commande.destination = Domaine.SYS_USB        
        return commande

    @staticmethod
    def cree_commande_liste_fichiers(nom_disque : str):
        commande = Commande(TypeCommande.LISTE_FICHIERS, { "nom_disque": nom_disque })
        CommandeFactory.__ajoute_source(commande)
        if nom_disque != Constantes.REPOSITORY:
            commande.destination = Domaine.SYS_USB
        else:
            commande.destination = Domaine.DOM0
        return commande
    
    @staticmethod
    def cree_commande_lit_fichier(nom_disque : str, chemin_fichier : str):
        arguments = {
            "nom_disque": nom_disque,
            "chemin_fichier": chemin_fichier
        }
        commande = Commande(TypeCommande.LIT_FICHIER, arguments)
        CommandeFactory.__ajoute_source(commande)
        commande.destination = Domaine.SYS_USB
        return commande
    
    @staticmethod
    def cree_commande_copie_fichier(source_disk:str, filepath:str, destination_disk:str):
        # Exemple :
        # { nom_fichier: "Mon Disque:/répertoire/fichier", nom_disque_destination: "Autre disque" }
        arguments = {
            "disk": source_disk,
            "filepath": filepath,
            "destination": destination_disk
        }
        commande = Commande(TypeCommande.COPIE_FICHIER, arguments)
        CommandeFactory.__ajoute_source(commande)
        commande.destination = Domaine.SYS_USB
        return commande
    
    @staticmethod
    def cree_commande_supprime_fichier(nom_fichier : str, nom_disque : str = Constantes().constante(Cles.DEPOT_LOCAL)):
        arguments = {
            "nom_fichier": nom_fichier,
            "nom_disque": nom_disque
        }
        commande = Commande(TypeCommande.COPIE_FICHIER, arguments)
        CommandeFactory.__ajoute_source(commande)
        commande.destination = Domaine.DOM0 if nom_disque == Constantes().constante(Cles.DEPOT_LOCAL) else Domaine.SYS_USB
        return commande
    
    @staticmethod
    def cree_commande_start_benchmark(id_benchmark: str, destination: str):
        arguments = {
            "id_benchmark": id_benchmark
        }
        commande = Commande(TypeCommande.START_BENCHMARK, arguments)
        CommandeFactory.__ajoute_source(commande)
        commande.destination = destination
        return commande

    @staticmethod 
    def cree_commande_get_file_footprint(filepath:str, disk:str) -> Commande:
        arguments = {
            "filepath": filepath,
            "disk": disk
        }
        commande = Commande(TypeCommande.GET_FILE_FOOTPRINT, arguments)
        CommandeFactory.__ajoute_source(commande)
        commande.destination = Domaine.DOM0 if disk == Constantes.REPOSITORY else Domaine.SYS_USB
        return commande
    
    @staticmethod
    def cree_commande_create_file(filepath:str, disk:str, contents:bytes) -> Commande:
        arguments = {
            "filepath": filepath,
            "disk": disk,
            "contents": contents
        }
        commande = Commande(TypeCommande.CREATE_FILE, arguments)
        CommandeFactory.__ajoute_source(commande)
        commande.destination = Domaine.DOM0 if disk == Constantes.REPOSITORY else Domaine.SYS_USB
        return commande

    ###
    # Fonctions privées
    #
    @staticmethod
    def __ajoute_source(commande):
        commande.source = Parametres().parametre(Cles.IDENTIFIANT_DOMAINE)
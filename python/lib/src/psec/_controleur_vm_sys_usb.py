from . import Constantes, Parametres, MessagerieDomu, Message, TypeMessage, Commande
from . import TypeCommande, FichierHelper, ReponseFactory, ErreurFactory
from . import Journal, Domaine, Cles, BenchmarkId
try:
    from . import DemonInputs
    from . import ControleurBenchmark
    NO_INPUTS_MONITORING = False
except:
    NO_INPUTS_MONITORING = True
    print("Importing ControleurVmSysUsb without inputs monitoring nor benchmarking capacity")
from . import NotificationFactory, FichierHelper
import logging, threading
from multiprocessing import Pool

class ControleurVmSysUsb():
    """ Cette classe traite les messages échangés par la sys-usb avec le Dom0 ou les autres domaines. """

    journal = Journal("Sys-usb controller")
    pool_tasks = None
    #files_copy_list = []

    def __init__(self):
        self.pool_tasks = Pool()

    def __del__(self):
        self.pool_tasks.terminate()

    def demarre(self, serial_port:str = ""):
        self.journal.info("Démarrage du Contrôleur du domaine sys-usb")

        # Démarrage de la messagerie
        MessagerieDomu().set_message_callback(self.__on_message_recu)
        MessagerieDomu().demarre(force_serial_port= serial_port)

        # Démarrage de la surveillance des entrées
        if NO_INPUTS_MONITORING != True:
            threading.Thread(target= self.__demarre_surveillance_entrees).start()

    def __demarre_surveillance_entrees(self):
        DemonInputs().demarre()

    def __on_message_recu(self, message : Message):
        """ Cette fonction traite les messages reçus sur l'interface de messagerie Xenbus. """

        self.journal.debug("Message reçu depuis le Xenbus : {}".format(message.to_json()))

        if message.type == TypeMessage.COMMANDE:
            threading.Thread(target=self.__traite_commande, args=(message,)).start()        

    def __traite_commande(self, commande: Commande):
        self.journal.debug("Traite la commande {}".format(commande.commande))

        if commande.commande == TypeCommande.LISTE_DISQUES:
            self.__get_liste_disques(commande)
        elif commande.commande == TypeCommande.LISTE_FICHIERS:
            self.__get_liste_fichiers(commande)
        elif commande.commande == TypeCommande.COPIE_FICHIER:
            self.journal.error("COPIE_FICHIER non impleménté")
            #self.__lit_fichier(commande)
        elif commande.commande == TypeCommande.LIT_FICHIER:
            self.__lit_fichier(commande)
        elif commande.commande == TypeCommande.SUPPRIME_FICHIER:
            self.__supprime_fichier(commande)
        elif commande.commande == TypeCommande.START_BENCHMARK and commande.destination == Domaine.SYS_USB:
            self.__execute_benchmark(commande.arguments.get("id_benchmark"), commande.source)    
        elif commande.commande == TypeCommande.GET_FILE_FOOTPRINT:
            filepath = commande.arguments.get("filepath")
            disk = commande.arguments.get("disk")
            self.__get_file_footprint(filepath, disk, commande.source)    
        elif commande.commande == TypeCommande.CREATE_FILE:
            filepath = commande.arguments.get("filepath")
            disk = commande.arguments.get("disk")
            contents = commande.arguments.get("contents")
            self.__get_create_file(filepath, disk, contents, commande.source)

    ####
    # Traitement des commandes
    #
    def __get_liste_disques(self, commande: Commande):
        self.journal.debug("Liste des disques demandée")
        # Récupère la liste des points de montage
        disques = FichierHelper.get_liste_disques()
        print(disques)

        # Génère la réponse
        reponse = ReponseFactory.cree_reponse_liste_disques(disques, commande.source)
        MessagerieDomu().envoie_message_xenbus(reponse)

    def __get_liste_fichiers(self, commande: Commande):
        # Vérifie les arguments de la commande
        arguments = commande.payload.get("arguments")
        nom_disque = arguments.get("nom_disque")
        if nom_disque == None:
            # S'il manque un argument on envoie une erreur
            self.__erreur("La commande est incomplète : il manque le nom du disque")            
            return

        # Récupère la liste des fichiers        
        fichiers = FichierHelper.get_liste_fichiers(nom_disque)

        # Génère la réponse
        reponse = ReponseFactory.cree_reponse_liste_fichiers(nom_disque, fichiers, commande.source)
        MessagerieDomu().envoie_message_xenbus(reponse)

    def __lit_fichier(self, commande: Commande):
        # La copie de fichier consiste à lire le fichier depuis le support externe
        # et à le placer dans le dépôt du système.
        # Une empreinte est calculée lors de la copie et transmise dans la réponse
        # Cette fonction est réentrante, le système gère le nombre de copies parallèles
        # en fonction des ressources disponibles.
        # Les arguments de la commande sont :
        # - nom_fichier au format disk:filename
        # - nom_disque_destination
        source_disk = commande.arguments.get("nom_disque")        
        source_file = commande.arguments.get("chemin_fichier")
        repository_path = Parametres().parametre(Cles.CHEMIN_DEPOT_DOM0)               
        source_filepath = "{}/{}/{}".format(Parametres().parametre(Cles.CHEMIN_MONTAGE_USB), source_disk, source_file)        
       
        self.pool_tasks.apply_async(self.__do_copy_file, (source_filepath, repository_path,))

    #def __copie_fichier(self, commande: Commande):
    #    pass

    def __supprime_fichier(self, commande: Commande):
        pass

    def __erreur(self, erreur : str):
        self.journal.error(erreur)
        err = ErreurFactory.genere_erreur(logging.ERROR, erreur)
        MessagerieDomu().envoie_erreur_xenbus(err)

    def __do_copy_file(self, source:str, destination: str):
        source_footprint = FichierHelper.calculate_footprint(source)

        if FichierHelper.copy_file(source, destination, source_footprint) == True:
            self.journal.info("La copie du fichier {} dans le dépôt s'est bien déroulée. L'empreinte est {}".format(source, source_footprint))
            # Envoi d'une notification
            notif = NotificationFactory.cree_notification_nouveau_fichier(source, destination, source_footprint)
        else:
            self.journal.error("La copie du fichier {} dans le dépôt a échoué.".format(source))

    def __execute_benchmark(self, id_benchmark:str, source:str):
        if id_benchmark == BenchmarkId.INPUTS:
            ControleurBenchmark().execute_benchmark_inputs(source)
        elif id_benchmark == BenchmarkId.FILES:
            ControleurBenchmark().execute_benchmark_fichiers(source)
        else:
            self.journal.error("L'identifiant de benchmark {} est inconnu".format(id_benchmark))

    def __get_file_footprint(self, filepath:str, disk:str, emetteur:str):
        self.journal.info("Calcul de l'empreinte numérique pour le fichier {} sur le disque {}".format(filepath, disk))

        mount_point = Parametres().parametre(Cles.CHEMIN_MONTAGE_USB)
        footprint = FichierHelper.calculate_footprint("{}/{}/{}".format(mount_point, disk, filepath))

        self.journal.info("Footprint = {}".format(footprint))

        reponse = ReponseFactory.cree_reponse_file_footprint(filepath, disk, footprint)
        reponse.destination = emetteur
        MessagerieDomu().envoie_message_xenbus(reponse)

    def __get_create_file(self, filepath:str, disk:str, contents:bytes, source:str):
        mount_point = Parametres().parametre(Cles.CHEMIN_MONTAGE_USB)
        
        complete_filepath = "{}/{}/{}".format(mount_point, disk, filepath)
        self.journal.debug("Création d'un fichier de {} octets à l'emplacement {}".format(len(contents), complete_filepath))

        reponse = None
        try:
            with open(complete_filepath, 'wb') as f:
                f.write(contents)
            f.close()
        except Exception as e:
            self.journal.error("Une erreur s'est produite lors de la création du fichier {}".format(complete_filepath))
            self.journal.error(e)
            reponse = ReponseFactory.cree_reponse_create_file(filepath, disk, "", False)
            return

        # On envoie la notification de succès
        footprint = FichierHelper.calculate_footprint(complete_filepath)
        reponse = ReponseFactory.cree_reponse_create_file(filepath, disk, footprint, True)
        reponse.destination = source
        MessagerieDomu().envoie_message_xenbus(reponse)
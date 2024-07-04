import os.path, logging, json
from . import SingletonMeta, Constantes, Cles, Domaine

class Parametres(metaclass=SingletonMeta):
    """Classe permettant de gérer les paramètres du système"""    

    # Par défaut, c'est le fichier de paramètres global qui est utilisé
    chemin_fichier_parametres = None
    params = {}

    def __init__(self):
        self.chemin_fichier_parametres = Constantes().constante("chemin_fichier_config_global")
        if self.__verifie_fichier_parametres(self.chemin_fichier_parametres):
            self.__lit_fichier()            

    def set_fichier_parametres(self, chemin):
        if self.__verifie_fichier_parametres(chemin):
            self.chemin_fichier_parametres = chemin
            self.__lit_fichier()
        else:
            print("Le fichier {} n'existe pas".format(chemin))

    def __verifie_fichier_parametres(self, chemin):
        return os.path.isfile(chemin)

    def __lit_fichier(self):
        print("Lecture du fichier de paramètres %s" % self.chemin_fichier_parametres)
        try:
            f = open(self.chemin_fichier_parametres)
            params = json.load(f)
            for cle in params:
                valeur = params[cle]
                if cle == Cles.NIVEAU_JOURNAL:
                    niv = Parametres.niveau_journalisation_from_string(valeur)
                    self.params[cle] = niv                    
                else:                    
                    self.params[cle] = valeur                    
        except OSError:
            # Afficher l'erreur
            pass

        #print(self.params)

    def parametre(self, cle):
        # D'abord on regarde dans le fichier local
        # puis dans les constantes
        valeur = self.params.get(cle)
        if valeur:
            return valeur          
        else:
            valeur = Constantes().constante(cle)
            if valeur:
                return valeur 
            else:
                print("AVERTISSEMENT : il n'y a aucun paramètre ni constante avec la clé %s" % cle)
                return None

    def set_parametre(self, cle, valeur):
        self.params[cle] = valeur

    def identifiant_domaine(self):
        try:
            return self.params[Cles.IDENTIFIANT_DOMAINE]
        except KeyError:
            print("AVERTISSEMENT : l'identifiant du domaine n'est pas défini.")
            return Domaine.INDEFINI
        
    @staticmethod
    def niveau_journalisation_from_string(niveau):
        if niveau == "DEBUG":
            return logging.DEBUG
        elif niveau == "INFO":
            return logging.INFO
        elif niveau == "WARN" or niveau == "WARNING":
            return logging.WARN        
        elif niveau == "ERREUR":
            return logging.ERROR
        elif niveau == "ERROR":
            return logging.ERROR
        elif niveau == "FATAL" or niveau == "CRITICAL":
            return logging.FATAL
        
    @staticmethod
    def niveau_journalisation_to_string(niveau):
        if niveau == logging.DEBUG:
            return "DEBUG"
        elif niveau == logging.INFO:
            return "INFO"
        elif niveau == logging.WARN:
            return "WARN"
        elif niveau == logging.ERROR:
            return "ERROR"
        elif niveau == logging.FATAL:
            return "FATAL"
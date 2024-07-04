class TypeCommande:
    INDEFINIE = "indefinie"
    LISTE_DISQUES = "liste_disques"
    LISTE_FICHIERS = "liste_fichiers"
    LIT_FICHIER = "lit_fichier"
    COPIE_FICHIER = "copie_fichier"
    SUPPRIME_FICHIER = "supprime_fichier"
    START_BENCHMARK = "start_benchmark"
    GET_FILE_FOOTPRINT = "get_file_footprint"
    CREATE_FILE = "create_file"

    @staticmethod
    def est_valide(type_commande : str):
        return (type_commande == TypeCommande.LISTE_DISQUES or type_commande == TypeCommande.LISTE_FICHIERS
            or type_commande == TypeCommande.LIT_FICHIER or type_commande == TypeCommande.COPIE_FICHIER 
            or type_commande == TypeCommande.SUPPRIME_FICHIER or type_commande == TypeCommande.START_BENCHMARK
            or type_commande == TypeCommande.GET_FILE_FOOTPRINT or type_commande == TypeCommande.CREATE_FILE)
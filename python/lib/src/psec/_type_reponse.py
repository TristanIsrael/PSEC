class TypeReponse:
    INDEFINI = "indefini"
    LISTE_DISQUES = "liste_disques"
    LISTE_FICHIERS = "liste_fichiers"    
    BENCHMARK_INPUTS = "benchmark_inputs"
    BENCHMARK_FILES = "benchmark_files"
    FILE_FOOTPRINT = "file_footprint"
    FILE_CREATION = "file_creation"

    @staticmethod
    def est_valide(type_reponse):
        return (type_reponse == TypeReponse.LISTE_DISQUES or type_reponse == TypeReponse.LISTE_FICHIERS
                or type_reponse == TypeReponse.BENCHMARK_INPUTS or type_reponse == TypeReponse.FILE_FOOTPRINT
                or type_reponse == TypeReponse.FILE_CREATION)
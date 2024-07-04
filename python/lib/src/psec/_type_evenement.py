class TypeEvenement:
    INDEFINI    = "indefini"
    DEBUG       = "debug"
    ETAT_DOMU   = "etat_domu"
    DISQUE      = "disque"
    FICHIER     = "fichier"
    ENTREE      = "entree"
    TEST        = "test"

    @staticmethod
    def est_valide(type_evenement):
        return type_evenement in (
            TypeEvenement.ETAT_DOMU
            , TypeEvenement.DISQUE 
            , TypeEvenement.ENTREE
            , TypeEvenement.DEBUG
            , TypeEvenement.FICHIER
            , TypeEvenement.TEST
        )
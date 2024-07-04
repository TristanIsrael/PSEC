class ErreurFactory():
    """Cette classe permet de générer une erreur au format JSON"""

    @staticmethod
    def genere_erreur(niveau : int, message : str) -> dict :
        j = {
            "error": 1,
            "niveau": niveau,
            "message": message
        }

        return j
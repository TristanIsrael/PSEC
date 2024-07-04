from Panoptiscan.lib.panoptiscan import _constantes
from Panoptiscan.lib.panoptiscan._journalisation import journalisation
from Panoptiscan.lib.panoptiscan.messagerie import messagerie_domu
from Panoptiscan.lib.panoptiscan import _parametres
import logging, os

def testcase_messagerie():
    _parametres.Parametres().set_fichier_parametres(os.path.dirname(os.path.realpath(__file__)) +"/configtest.conf")
    j = journalisation.Journal()
    assert j.get_niveau_journalisation() == logging.DEBUG
    assert j.get_chemin_journal() == "/tmp/test.log"
    j.inscrit_message(logging.DEBUG, "Message de test")
    print()

    # Tests de la classe Messagerie
    print("Tests de la messagerie")
    c = messagerie_domu.Commande("test_commande", {"bla": "bli"})
    #c.print()
    assert c.type == messagerie_domu.TypeMessage.COMMANDE
    assert c.source == "vm_test"
    assert c.destination == _constantes.Constantes.Domaine.INDEFINI
    assert c.payload["commande"] == "test_commande"
    assert c.payload["arguments"]["bla"] == "bli"

    

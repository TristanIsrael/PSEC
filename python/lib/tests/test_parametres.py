from Panoptiscan.lib.panoptiscan import _constantes
from Panoptiscan.lib.panoptiscan import _parametres
import os

def testcase_parametres():
    # Tests de la classe Parametres
    p1 = _parametres.Parametres()
    p2 = _parametres.Parametres()

    print("Tests de la classe Parametres")
    assert p1 == p2
    assert p1.chemin_fichier_parametres == "/etc/panoptiscan/global.conf"

    _parametres.Parametres().set_fichier_parametres( os.path.dirname(__file__) +"/configtest.conf" )
    assert p1.parametre("toto") == None
    assert _parametres.Parametres().parametre(_constantes.Cles.CHEMIN_SOCKET_XENBUS_DOMU) == "/tmp/xenbus.sock"
    print()
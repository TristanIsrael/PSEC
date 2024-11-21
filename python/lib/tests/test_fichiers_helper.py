import os, sys

# Ajout du répertoire de la bibliothèque
curdir = os.path.dirname(__file__)
libdir = os.path.realpath(curdir+"/../src")
sys.path.append(libdir)

from panoptiscan_lib import FichierHelper, Parametres, Cles

def testcase_lit_arborescence():
    Parametres().set_parametre(Cles.CHEMIN_MONTAGE_USB, "/Users/tristan/Downloads/Temp")
    liste = FichierHelper.get_liste_fichiers("")
    print(liste)

if __name__ == "__main__":
    testcase_lit_arborescence()
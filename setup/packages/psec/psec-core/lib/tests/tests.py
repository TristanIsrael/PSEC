import os, sys

# Ajout du répertoire de la bibliothèque
curdir = os.path.dirname(__file__)
libdir = os.path.realpath(curdir+"/../src")
sys.path.append(libdir)

import test_journalisation
#from panoptiscan_lib import Journalisation 

#Parametres().set_fichier_parametres("{}/configtest.conf".format(curdir))

#test_parametres.testcase_parametres()
#test_journalisation.testcase_journalisation()
test_journalisation.testcase_journal_proxy()
#test_surveillance_disque.testcase_surveille_tmp()
#test_messagerie.testcase_messagerie()

#tu = test_messagerie_domu.TestMessagerieDomu()
#tu.exec()

#tu = test_messagerie_dom0.TestMessagerieDom0()
#tu.exec()

#tu = test_api_domu.TestAPIDomu()
#tu.exec()

#test_fichiers_helper.testcase_lit_arborescence()
#test_fichiers_helper.testcase_commande_liste_fichiers()
from panoptiscan_lib import Journal, JournalProxy, Constantes, Domaine
import logging, os

def testcase_journalisation():
    # Tests de la classe Journalisation
    print("Tests de la journalisation")
    j = Journal(entite= "Test Journalisation", domaine= Domaine.DOM0)
    assert j.get_niveau_journalisation() == logging.DEBUG
    j.debug("Message de test local sans inscription")
    j.info("Ce message s'ajoutera au fichier")
    j.error("Ce message ne s'ajoutera pas au fichier")

def testcase_journal_proxy():
    print("Test du proxy")

    j = JournalProxy()
    j.demarre()

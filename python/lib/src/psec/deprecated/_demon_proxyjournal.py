import os, sys
#import daemon
#from daemon import pidfile
from . import JournalProxy, Parametres, Cles

class DemonProxyJournal():
    """ Cette classe gère les message de journal arrivant des DomU et du Dom0 et les concatène dans un fichier unique locale """    

    #def demarre(self):
    #    chemin_fichiers_pid = Parametres().parametre(Cles.CHEMIN_FICHIERS_PID)
    #    with daemon.DaemonContext(
    #        stdout=sys.stdout,
    #        stderr=sys.stderr,
    #        pidfile=pidfile.TimeoutPIDLockFile("{}/panoptiscan-journal-proxy.pid".format(chemin_fichiers_pid))
    #        ):
    #        self.demarre_proxy()
        
    def demarre(self):
        JournalProxy().demarre()
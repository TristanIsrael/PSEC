import QtQuick
import net.alefbet

PanneauDisquesUi {
    id: root

    /** Slots */
    Connections {
        target: InterfaceSocle
        function onDisksChanged() {
            AppController.debug("La liste des disques a changé")
            AppController.debug(InterfaceSocle.disks)
        }
        function onTestFinished(success, errorStr) {
            if(success)
                lblEmpreinteOk = "OK"
            else 
                lblEmpreinteOk = errorStr
        }
    }

    Connections {
        target: btnDownload
        function onClicked() {
            AppController.debug("Téléchargement du fichier %1%2/%3 demandé".arg(selectedDisk).arg(selectedFolder).arg(selectedFile))
            InterfaceSocle.download_file(selectedDisk, selectedFolder, selectedFile)
        }
    }

    Connections {
        target: btnStartTests
        function onClicked() {
            AppController.debug("Démarrage des tests")
            AppController.start_test()
        }
    }

    function onReloadContent() {
        AppController.debug("Rechargement de la liste des disques USB demandé")
        InterfaceSocle.get_liste_disques()
    }

    Component.onCompleted: function() {
        AppController.debug("Demande la liste des disques")
        InterfaceSocle.get_liste_disques()
    }

    /** Fonctions */
    function afficheContenuDisque(nom, etat) {

    }
    
}
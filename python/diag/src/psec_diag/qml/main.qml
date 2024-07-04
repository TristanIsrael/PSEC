import QtQuick
import net.alefbet

EcranPrincipal {
    id: window

    /** Slots */
    /*Connections {
        target: AppController
        function onMouseXChanged() {
            console.debug(AppController.mouseX)
        }
        function onMouseYChanged() {
            console.debug(AppController.mouseY)
        }
    }*/

    Component.onCompleted: {
        if(force_paysage) {
            mode_paysage = force_paysage
        }

        console.log("Mode paysage activé : " + (mode_paysage ? "Oui" : "Non"))
        console.log("Fonctionne sur " +Qt.platform.os)
    }    

    onWidthChanged: {
        if( (window.width < window.height) && !mode_paysage ) {            
            console.log("Bascule automatique en mode paysage")
            mode_paysage = true   
        }
    }

    onVisibilityChanged: {  
        if(visible)      
            console.debug("Résolution : " +Qt.application.screens[0].width +"x" +Qt.application.screens[0].height)
    }

}
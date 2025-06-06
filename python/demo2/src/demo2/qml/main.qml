import QtQuick
import QtQuick.Controls
import net.alefbet

ApplicationWindow {
    id: window

    property bool mode_paysage: width < height

    width: 600
    height: 300
    visible: true    

    font.family: "Roboto"
    font.pointSize: 18

    MainScreen {
        id: mainScreen
        anchors.fill: parent        
    }

    Component.onCompleted: {
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
            console.log("Résolution : " +Qt.application.screens[0].width +"x" +Qt.application.screens[0].height)
    }

    Connections {
        target: mainScreen.btnDemarrer
        onClicked: AppController.on_btn_start_clicked(mainScreen.fldMessage.text)
    }
}

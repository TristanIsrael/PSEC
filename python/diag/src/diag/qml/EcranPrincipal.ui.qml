import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import net.alefbet

ApplicationWindow {
    id: window

    property bool mode_paysage: force_paysage | (width < height)

    width: Screen.desktopAvailableWidth
    height: Screen.desktopAvailableHeight
    visible: true
    visibility: Window.FullScreen

    font.family: "Roboto"
    font.pointSize: 18

    Rectangle {
        color: "#ccc"
        anchors {
            fill: parent
        }        

        ColumnLayout {    
            anchors {
                fill: parent
                margins: 20
            }
            spacing: 10

            PanneauInputs { 
                id: pnlInputs
                Layout.preferredWidth: parent.width
            }            
            
            PanneauDisques { 
                id: pnlDisks
                Layout.preferredWidth: parent.width
                Layout.preferredHeight: (parent.height-pnlInputs.height)/2
            }

            PanneauDepot {
                id: pnlRepository
                Layout.preferredWidth: parent.width                
                Layout.preferredHeight: (parent.height-pnlInputs.height)/2
            }
            
        }
    }    

    /*Timer {
        interval: 1000
        running: true
        onTriggered: {
            AppController.simule_souris()
        }
    }*/
}


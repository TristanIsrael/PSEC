import QtQuick
import Components
import Safecor

Item {
    id: root

    /* Internal properties */    
    width: implicitWidth
    height: implicitHeight
    implicitWidth: Environment.mainWidth
    implicitHeight: Environment.mainHeight

    MainScreenUi {
        id: window

        anchors.fill: parent
        backFilter.colorizationColor: bindings.systemStateColor

        /* Slots */
        Connections {
            target: window.btnStartStop
            function onClicked() {
                AppController.start_stop();
            }
        }
    }

    Bindings {
        id: bindings
    }

}


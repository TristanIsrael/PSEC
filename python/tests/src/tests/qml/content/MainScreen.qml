import QtQuick
import Components

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
    }

    Bindings {
        id: bindings
    }

}


import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Components
import Panels.Compatibility
import Panels.Storage
import Panels.Performance

Rectangle {
    color: Colors.background

    anchors {
        fill: parent
    }

    Rectangle {
        id: frame
        anchors {
            fill: parent
            margins: 10
        }

        color: "transparent"
        border {
            color: Colors.cyan
            width: 1
        }
    }

    Rectangle {
        anchors {
            horizontalCenter: title.horizontalCenter
        }
        width: title.width + 20
        height: title.height
        color: parent.color
    }

    PText {
        id: title
        anchors {
            horizontalCenter: parent.horizontalCenter
        }
        text: qsTr("PSEC Diagnostics")
        font.pixelSize: 18
    }

    TabBar {
        id: tabs

        height: 35
        background: Item {}
        
        anchors {
            left: frame.left
            leftMargin: 5
            right: frame.right
            rightMargin: 5
            top: title.bottom
            topMargin: 10
        }

        PTabButton {
            text: qsTr("Compatibility")
        }

        PTabButton {
            text: qsTr("Storage")
        }

        PTabButton {
            text: qsTr("Performance")
        }
        
    }

    StackLayout {
        anchors {
            left: frame.left
            right: frame.right
            bottom: frame.bottom
            top: tabs.bottom
            margins: 5
        }
        currentIndex: tabs.currentIndex

        CompatibilityPanel { }

        StoragePanel {}

        PerformancePanel {}
    }

}

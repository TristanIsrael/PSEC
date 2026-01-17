import QtQuick
import QtQuick.Controls
import Components

Item {
    id: root

    property int progress: 0 // 0-100
    property alias label: lbl.text
    property bool success: true
    property bool isPackage: false

    width: implicitWidth
    height: implicitHeight
    implicitHeight: 30
    implicitWidth: 400

    Rectangle {
        id: rctBack
        radius: height * 0.2
        color: {
            if(root.progress === 100) {
                return root.success ? Environment.colorSuccess : Environment.colorFailure
            }

            return Environment.colorRunning
        }
        height: parent.height
        width: parent.implicitWidth * progress / 100
    }

    Text {
        id: lbl
        anchors {
            fill: parent
            leftMargin: root.isPackage ? 10 : 20
            rightMargin: parent.height * 0.2
            topMargin: parent.height * 0.2
            bottomMargin: parent.height * 0.2
        }
        horizontalAlignment: Qt.AlignLeft
        verticalAlignment: Qt.AlignVCenter
        fontSizeMode: Text.HorizontalFit
        font.pixelSize: height * (root.isPackage ? 1 : 0.8)
        text: qsTr("Progress component")
        color: Environment.colorText
    }
}

import QtQuick
import QtQuick.Controls

Button {
    id: control

    text: "button"
    implicitHeight: 35
    height: implicitHeight

    contentItem: Text {
        id: lbl
        text: control.text
        font {
            weight: Font.Bold
            pixelSize: 16
        }
        opacity: enabled ? 1.0 : 0.3
        color: Colors.black
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        anchors.fill: parent
        color: Colors.cyan
    }
}

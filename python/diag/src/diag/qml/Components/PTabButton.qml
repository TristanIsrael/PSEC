import QtQuick
import QtQuick.Controls

TabButton {
    id: control

    text: "button"
    implicitHeight: 35
    height: implicitHeight

    contentItem: Text {
        id: lbl
        text: control.text
        font {
            weight: control.checked ? Font.Bold : Font.Normal
            pixelSize: 16
        }
        opacity: enabled ? 1.0 : 0.3
        color: control.checked ? Colors.black : Colors.cyan
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        anchors.fill: parent
        color: control.checked ? Colors.cyan : "transparent"
    }
}

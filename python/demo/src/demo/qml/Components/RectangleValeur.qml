import QtQuick

Rectangle {
    id: root

    property string text
    readonly property int margin: 10

    color: "#111"
    implicitWidth: txt.implicitWidth+margin
    implicitHeight: txt.implicitHeight+margin
    width: implicitWidth
    height: implicitHeight

    Text {
        id: txt
        anchors.centerIn: parent
        text: root.text
        color: "white"
    }
}
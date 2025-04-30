import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    property string text: qsTr("Capability")
    property alias state: stt.text
    property alias stateColor: stt.color
    property alias stateDescription: stDesc.text

    implicitWidth: clyt.width
    implicitHeight: clyt.height

    ColumnLayout {
        id: clyt

        RowLayout {
            id: rlyt

            PText {
                id: lbl
                text: root.text + qsTr(":")
                font.bold: true
            }

            PText {
                id: stt
                text: qsTr("Unknown")
                color: Colors.white
            }
        }

        Rectangle {
            color: Colors.black
            height: stDesc.text !== "" ? stDesc.height : 0
            width: stDesc.width
            visible: stDesc.text !== ""

            PText {
                id: stDesc
                padding: 5
            }
        }
    }
}

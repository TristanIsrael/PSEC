import QtQuick 
import QtQuick.Layouts
import Components

Rectangle {
    color: Colors.background

    ColumnLayout {
        anchors.fill: parent
        spacing: 20

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: lblDescription.height *2
            color: Colors.black

            PText {
                id: lblDescription
                anchors.centerIn: parent
                font.pixelSize: 20

                text: qsTr("This panel offers different benchmark tests to measure the system performance.")
            }
        }

        Item {
            Layout.fillHeight: true
        }
    }
}
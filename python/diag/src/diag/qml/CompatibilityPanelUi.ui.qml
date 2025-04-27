import QtQuick 
import QtQuick.Layouts

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

                text: qsTr("This panel indicates whether the current execution platform is compatible with PSEC and which functions will be available.")
            }
        }

        Item {
            Layout.fillHeight: true
        }
    }
}
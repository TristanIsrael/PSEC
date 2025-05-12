import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Components

Rectangle {
    id: root

    property alias fldMessage: fldMessage
    property alias btnDemarrer: btnDemarrer    
    property alias fldResult: fldResult

    implicitWidth: 600
    implicitHeight: 300

    color: Colors.background

    ColumnLayout {
        anchors {
            fill: parent 
            margins: 20
        }

        RowLayout {        
            Layout.fillWidth: true
            Layout.fillHeight: true

            PText {
                text: qsTr("Message :")
            }        

            TextField {
                id: fldMessage
                Layout.fillWidth: true
                placeholderText: qsTr("Veuillez saisir votre message :")
            }
        }

        
        PText {
            text: qsTr("Résultat")
        }

        TextEdit {
            id: fldResult
            Layout.fillWidth: true
            Layout.fillHeight: true
            readOnly: true 
            color: Colors.white
        }

        PButton {
            id: btnDemarrer
            text: qsTr("Démarrer")
            Layout.alignment: Qt.AlignHCenter            
        }
    }
}

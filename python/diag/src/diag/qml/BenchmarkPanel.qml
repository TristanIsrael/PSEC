import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    

    GridLayout {
        anchors.fill: parent
        columns: 2

        Button {
            id: btnStartBenchmark
            Layout.columnSpan: 2
            Layout.alignment: Qt.AlignHCenter
            text: qsTr("Démarrer")
        }                

        Label {
            horizontalAlignment: Label.AlignRight
            font.bold: true
            text: qsTr("Durée émission")
        }

        Label {
            text: "%1 ms".arg(dureeEmission)
        } 

        Label {
            horizontalAlignment: Label.AlignRight
            font.bold: true
            text: qsTr("Durée réception")
        }

        Label {
            text: "%1 ms".arg(dureeReception)
        }

        Label {
            horizontalAlignment: Label.AlignRight
            font.bold: true
            text: qsTr("Itérations émises")
        }

        Label {
            text: "%1".arg(iterationsEmises)
        }

        Label {
            horizontalAlignment: Label.AlignRight
            font.bold: true
            text: qsTr("Itérations reçues")
        }

        Label {
            text: "%1".arg(iterationsRecues)
        }

        Label {
            horizontalAlignment: Label.AlignRight
            font.bold: true
            text: qsTr("Débit général")
        }

        Label {
            text: "%1/cs".arg(debitGeneral)
        }

        Label {
            horizontalAlignment: Label.AlignRight
            font.bold: true
            text: qsTr("Débit courant")
        }

        Label {
            text: "%1/cs".arg(debitCourant)
        }            
    }
}

import QtQuick
import QtQuick.Controls 
import QtQuick.Layouts
import net.alefbet

RowLayout {
    property double debitEcritureUSB10Ko: 0.0
    property double debitEcritureUSB100Ko: 0.0
    property double debitEcritureUSB500Ko: 0.0
    property double debitEcritureUSB1Mo: 0.0
    property double debitEcritureUSB10Mo: 0.0
    property double debitEcritureUSB100Mo: 0.0
    property double debitLectureUSB10Ko: 0.0
    property double debitLectureUSB100Ko: 0.0
    property double debitLectureUSB500Ko: 0.0
    property double debitLectureUSB1Mo: 0.0
    property double debitLectureUSB10Mo: 0.0
    property double debitLectureUSB100Mo: 0.0
    property double debitEcritureDepot10Ko: 0.0
    property double debitEcritureDepot100Ko: 0.0
    property double debitEcritureDepot500Ko: 0.0
    property double debitEcritureDepot1Mo: 0.0
    property double debitEcritureDepot10Mo: 0.0
    property double debitEcritureDepot100Mo: 0.0

    property alias btnStartBenchmark: btnStartBenchmark
    property alias grpDepot: grpDepot

    //implicitHeight: grpDepot.height+spacing+grpBenchmark.height
    spacing: 10

    Group {
        id: grpDepot

        //Layout.preferredHeight: parent.height        
        //Layout.preferredHeight: Math.max(grpBenchmark.implicitHeight, implicitHeight) 
        //Layout.preferredWidth: parent.width - grpBenchmark.width - parent.spacing
        title: qsTr("Dépôt")
        reloadable: true
        Layout.fillHeight: true
        Layout.fillWidth: true

        Label {
            id: lblVide
            text: qsTr("Le dépôt est vide")
            visible: pnlFile.count === 0
        }

        RowLayout {
            anchors.fill: parent
            spacing: 10
            visible: pnlFile.count > 0
            
            PanneauFichiers {  
                id: pnlFile   
                disk: "__repository__"
                Layout.fillHeight: true
                Layout.fillWidth: true           
            }
            
        }
    }

    Group {    
        id: grpBenchmark
        title: qsTr("Benchmark")    
        //Layout.preferredHeight: Math.max(grpDepot.implicitHeight, implicitHeight)     
        Layout.fillHeight: true

        GridLayout {     
            columns: 7
            columnSpacing: 10

            Button {
                id: btnStartBenchmark
                Layout.columnSpan: 7
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("Démarrer")
            }  

            //Line 1
            Text {} 
            Text { text: qsTr("10 Ko") }
            Text { text: qsTr("100 Ko") }
            Text { text: qsTr("500 Ko") }
            Text { text: qsTr("1 Mo") }
            Text { text: qsTr("10 Mo") }
            Text { text: qsTr("100 Mo") }

            //Line write to USB
            Text { text: qsTr("Ecriture USB") }
            Text { text: qsTr("%1 Mo/s").arg(debitEcritureUSB10Ko.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitEcritureUSB100Ko.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitEcritureUSB500Ko.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitEcritureUSB1Mo.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitEcritureUSB10Mo.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitEcritureUSB100Mo.toFixed(2)) }

            //Line read from USB
            Text { text: qsTr("Lecture USB") }
            Text { text: qsTr("%1 Mo/s").arg(debitLectureUSB10Ko.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitLectureUSB100Ko.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitLectureUSB500Ko.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitLectureUSB1Mo.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitLectureUSB10Mo.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitLectureUSB100Mo.toFixed(2)) }

            //Line write to repository
            Text { text: qsTr("Ecriture dépôt") }
            Text { text: qsTr("%1 Mo/s").arg(debitEcritureDepot10Ko.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitEcritureDepot100Ko.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitEcritureDepot500Ko.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitEcritureDepot1Mo.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitEcritureDepot10Mo.toFixed(2)) }
            Text { text: qsTr("%1 Mo/s").arg(debitEcritureDepot100Mo.toFixed(2)) }
                     
        }
    }
}
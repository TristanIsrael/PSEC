import QtQuick
import QtQuick.Controls 
import QtQuick.Layouts
import net.alefbet

RowLayout {
    id: root     

    property alias btnDownload: btnDownload
    property alias btnStartTests: btnStartTests
    property alias lblEmpreinteOk: lblEmpreinteOk
    property string selectedDisk
    property string selectedFolder
    property string selectedFile

    spacing: 10
    //implicitHeight: grpDisques.height

    Group {
        id: grpDisques
        title: qsTr("USB")
        reloadable: true 
        signal resetSelection(string disk)
        Layout.preferredHeight: parent.height
        Layout.preferredWidth: parent.width - grpTests.width - parent.spacing

        Label {
            id: lblVide
            text: qsTr("Aucun périphérique USB connecté")
            visible: InterfaceSocle.disks.length === 0
        }

        RowLayout {
            anchors.fill: parent
            spacing: 10
            visible: InterfaceSocle.disks.length > 0
        
            Repeater {
                model: InterfaceSocle.disks
                height: parent.height

                PanneauFichiers {  
                    id: pnlFile   
                    disk: modelData
                    Layout.fillHeight: true
                    Layout.fillWidth: true    

                    Connections {
                        function onSelectedFileChanged() {
                            //btnDownload.enabled = selectedFile !== ""
                            if(selectedFile !== "") {
                                root.selectedDisk = disk 
                                root.selectedFolder = currentFolder
                                root.selectedFile = selectedFile
                                btnDownload.enabled = true                            
                                root.resetSelection(disk)
                            }
                        }  
                        Component.onCompleted: function() {
                            root.resetSelection.connect(pnlFile.onResetSelection)
                        }                  
                    }            
                }
            }

            ColumnLayout {
                Button {
                    id: btnDownload
                    text: qsTr("Télécharger")
                    enabled: false                
                }
            }
        }
    }

    Group {
        id: grpTests
        title: qsTr("Tests")
        Layout.preferredHeight: parent.height

        GridLayout {
            columns: 2

            Button {
                id: btnStartTests
                Layout.columnSpan: 2
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("Démarrer")
            }

            Text {
                text: qsTr("Empreinte :")
            }

            Text {
                id: lblEmpreinteOk
                text: qsTr("Non exécuté")                
            }
        }
    }
}
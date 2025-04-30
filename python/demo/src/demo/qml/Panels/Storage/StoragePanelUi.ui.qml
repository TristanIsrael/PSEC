import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import net.alefbet
import Components

Rectangle {
    color: Colors.background

    ColumnLayout {
        anchors.fill: parent
    
        Rectangle {
            Layout.preferredWidth: parent.width
            Layout.preferredHeight: lblDescription.height *2
            color: Colors.black

            PText {
                id: lblDescription
                anchors.centerIn: parent
                font.pixelSize: 20

                text: qsTr("This panel offers a file browser to test PSEC storage capabilities.")
            }
        }

        RowLayout {
            id: pnlSelection

            Layout.fillWidth: true
            Layout.fillHeight: true
          
            DisksList {
                id: pnlDisks
                Layout.preferredWidth: parent.width /5
                Layout.fillHeight: true
            }

            FilesList {
                id: pnlFiles
                selectedDisk: pnlDisks.selectedDisk
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }

        Rectangle {
            id: pnlActions

            Layout.fillWidth: true
            Layout.preferredHeight: pnlActionsContent.height * 1.5

            RowLayout {
                id: pnlActionsContent

                anchors {
                    verticalCenter: parent.verticalCenter
                    left: parent.left
                    leftMargin: 10
                    right: parent.right
                    rightMargin: 10
                }

                spacing: 15

                PButton {
                    id: btnStartBenchmark
                    enabled: false //InterfaceSocle.disks.length > 1
                    text: qsTr("Run benchmark")
                }

                PButton {
                    id: btnGetFile
                    enabled: false
                    //enabled: pnlFiles.selectedFile !== "" && (pnlDisks.selectedDisk !== "__repository__" && pnlDisks.selectedDisk !== "")
                    text: qsTr("Get file")
                }

                PButton {
                    id: btnPutFile
                    enabled: false
                    //enabled: pnlFiles.selectedFile !== "" && (pnlDisks.selectedDisk !== "__repository__" && pnlDisks.selectedDisk !== "")                
                    text: qsTr("Put file")
                }

                PButton {
                    id: btnDeleteFile
                    enabled: false
                    //enabled: pnlFiles.selectedFile !== "" && pnlDisks.selectedDisk !== ""
                    text: qsTr("Delete file")
                }

                Item {
                    Layout.fillWidth: true
                }
            }
        }
    }
}

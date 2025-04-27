import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import net.alefbet

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
            /*anchors {
                left: parent.left
                leftMargin: 10
                top: parent.top
                topMargin: 10
                right: parent.right
                rightMargin: 10
                bottom: pnlActions.top
                bottomMargin: 10
            }*/

            DisksList {
                id: pnlDisks
                Layout.preferredWidth: parent.width * 0.3
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
            /*anchors {
                bottom: parent.bottom
                left: parent.left
                right: parent.right
            }*/
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
                    enabled: pnlFiles.selectedFile !== "" && (pnlDisks.selectedDisk !== "__repository__" && pnlDisks.selectedDisk !== "")
                    text: qsTr("Get file")
                }

                PButton {
                    id: btnPutFile
                    enabled: pnlFiles.selectedFile !== "" && (pnlDisks.selectedDisk !== "__repository__" && pnlDisks.selectedDisk !== "")                
                    text: qsTr("Put file")
                }

                PButton {
                    id: btnDeleteFile
                    enabled: pnlFiles.selectedFile !== "" && pnlDisks.selectedDisk !== ""
                    text: qsTr("Delete file")
                }

                Item {
                    Layout.fillWidth: true
                }
            }
        }
    }
}

/*RowLayout {
    id: root

    property alias btnDownload: btnDownload
    property alias btnStartTests: btnStartTests
    property alias lblEmpreinteOk: lblEmpreinteOk
    property string selectedDisk
    property string selectedFolder
    property string selectedFile

    spacing: 10

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

                StoragePanel {
                    id: pnlFile
                    disk: modelData
                    Layout.fillHeight: true
                    Layout.fillWidth: true

                    Connections {
                        function onSelectedFileChanged() {
                            //btnDownload.enabled = selectedFile !== ""
                            if (selectedFile !== "") {
                                root.selectedDisk = disk
                                root.selectedFolder = currentFolder
                                root.selectedFile = selectedFile
                                btnDownload.enabled = true
                                grpDisques.resetSelection(disk)
                            }
                        }
                        Component.onCompleted: function () {
                            grpDisques.resetSelection.connect(
                                        pnlFile.onResetSelection)
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
*/


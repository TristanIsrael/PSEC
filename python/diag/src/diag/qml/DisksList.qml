import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import net.alefbet

Rectangle {
    id: root

    property string selectedDisk //: "__repository__"

    implicitWidth: 200
    implicitHeight: 600
    clip: true

    color: Colors.background
    border {
        width: 1
        color: Colors.cyan
    }

    ColumnLayout {
        id: lyt
        anchors {
            fill: parent
            margins: 10
        }

        x: 5
        y: 5
        spacing: 10

        Repeater {
            anchors.fill: parent
            model: InterfaceSocle.disks
            //model: [ "__repository__", "Disk 1", "Disk 2", "Disk 3" ]

            Rectangle {
                width: parent.width
                height: txt.implicitHeight
                color: modelData === root.selectedDisk ? Colors.cyan : "transparent"

                PText {
                    id: txt
                    color: modelData === root.selectedDisk ? Colors.black : Colors.cyan
                    text: modelData === "__repository__" ? qsTr("Local Storage") : modelData
                    font {
                        family: "Courier"
                        weight: Font.Bold
                        pixelSize: 16
                    }
                }

                MouseArea {
                    anchors.fill: parent 

                    onClicked: function() {
                        root.selectedDisk = modelData
                    }
                }
            }
        }

        Item {
            Layout.fillHeight: true
        }
    }

    Connections {
        target: InterfaceSocle

        function onDisksChanged() {
            AppController.debug("Disks list changed")
            AppController.debug(InterfaceSocle.disks)
            root.selectedDisk = InterfaceSocle.disks[0]
        }

        function onTestFinished(success, errorStr) {
            if(success)
                lblEmpreinteOk = "OK"
            else 
                lblEmpreinteOk = errorStr
        }
    }

    Component.onCompleted: function() {
        AppController.debug("Demande la liste des disques")
        InterfaceSocle.get_disks_list()
    }

}

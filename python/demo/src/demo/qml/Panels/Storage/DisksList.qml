import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Components
import net.alefbet

Rectangle {
    id: root

    property string selectedDisk

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
            Layout.fillHeight: true
            Layout.preferredWidth: parent.width
            model: InterfaceSocle.disks

            Rectangle {
                width: parent.width
                height: txt.height
                color: modelData === root.selectedDisk ? Colors.cyan : "transparent"

                PText {
                    id: txt
                    color: modelData === root.selectedDisk ? Colors.black : Colors.cyan
                    text: modelData === "__repository__" ? qsTr("Repository") : modelData
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
                        InterfaceSocle.get_disk_content(root.selectedDisk, "")
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
            root.selectedDisk = InterfaceSocle.disks[0]
            InterfaceSocle.get_disk_content(root.selectedDisk, "")
        }
        
    }

    Component.onCompleted: function() {
        AppController.debug("Demande la liste des disques")
        InterfaceSocle.get_disks_list()
    }

}

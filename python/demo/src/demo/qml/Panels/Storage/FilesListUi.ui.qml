import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Components

Rectangle {
    id: root

    property string selectedDisk
    property string selectedFile
    property alias listView: listView

    signal itemClicked(int row, string fileType, string path, string fileName)

    implicitWidth: 800
    implicitHeight: 600
    clip: true

    color: Colors.background
    border {
        width: 1
        color: Colors.cyan
    }

    ListView {
        id: listView

        anchors {
            fill: parent
            margins: 10
        }

        x: 5
        y: 5
        spacing: 10
        clip: true

        ScrollBar.vertical: ScrollBar {
            id: vScrollBar
        }

        model: templateModel

        anchors {
            fill: parent
            topMargin: 5
            leftMargin: 10
        }

        delegate: Rectangle {
            property bool selected: root.selectedFile === fileName
            color: selected ? Colors.cyan : "transparent"
            width: ListView.view.width - ListView.view.anchors.leftMargin - vScrollBar.width
            height: lyt.height + 6

            RowLayout {
                id: lyt
                y: 3

                height: 20

                Item {
                    width: 2
                }

                /*Image {
                    source: fileType === "file" ? "../images/file.png" : fileType === "special_up" ? "../images/folder_up.png" : "../images/folder.png"
                    sourceSize.width: 16
                    sourceSize.height: 16
                }*/
                StorageIcon {
                    Layout.preferredWidth: 16
                    Layout.preferredHeight: 16
                    type: fileType
                }

                PText {
                    id: lblFilename
                    text: fileName
                    color: selected ? Colors.black : Colors.cyan
                    font {
                        family: "Courier"
                        weight: Font.Bold
                        pixelSize: 16
                    }
                }
            }

            MouseArea {
                anchors.fill: parent

                Connections {
                    function onClicked() {
                        root.selectedFile = fileName
                        root.itemClicked(index, fileType, path, fileName)
                    }
                }
            }
        }
    }
}

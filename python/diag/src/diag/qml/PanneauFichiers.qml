import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import net.alefbet

Rectangle {
    id: root
    color: "#ddd"
    radius: 3

    property string disk    
    property string selectedFile
    property string currentFolder
    property int count: lv.count
    
    Label {
        id: lbl
        anchors {
            top: parent.top 
            left: parent.left 
            right: parent.right 
            margins: 5
        }
        font.bold: true
        text: disk !== "__repository__" ? qsTr("Disque %1").arg(modelData) : ""
        visible: disk !== "__repository__"
        height: visible ? implicitHeight : 0
    }

    ListView {
        id: lv
        clip: true

        ScrollBar.vertical: ScrollBar { 
            id: vScrollBar
        }

        model: DiskProxyModel {
            source: DiskModel
            disk: root.disk
        }
        anchors {
            top: lbl.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            topMargin: 5
            leftMargin: 10
        }
        spacing: 2

        delegate:    
            Rectangle {                
                color: "transparent"
                border {
                    color: selectedFile == fileName ? "#88abf6" : "transparent"
                    width: 2
                }
                radius: 2
                width: ListView.view.width - ListView.view.anchors.leftMargin - vScrollBar.width
                height: lyt.height + 6       

                RowLayout {
                    id: lyt
                    y: 3
                    
                    height: 20

                    Item {
                        width: 2
                    }

                    Image {
                        source: fileType === "file" ? "../images/file.png" : fileType === "special_up" ? "../images/folder_up.png" : "../images/folder.png"
                        sourceSize.width: 16
                        sourceSize.height: 16                        
                    }

                    Label {
                        id: lblFilename
                        text: fileName                        
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: function() {
                        if(fileType === "special_up") {
                            AppController.debug("Up")
                            lv.model.go_up()
                            selectedFile = ""
                        } else if(fileType === "folder") {
                            AppController.debug("Afficher %1".arg(lblFilename.text))
                            lv.model.folder = lblFilename.text
                            currentFolder = lv.model.folder
                            selectedFile = ""
                        } else if(fileType === "file") {
                            selectedFile = lblFilename.text
                        }
                    }
                }
            }
    }
    
    function onResetSelection(disk) {
        if(disk !== "" && disk !== root.disk) {
            AppController.debug("Reset selection on %1. (disk=%2)".arg(root.disk).arg(disk))
            root.selectedFile = ""
        }
    }
}
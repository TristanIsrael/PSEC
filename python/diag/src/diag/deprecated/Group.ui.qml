import QtQuick
import QtQuick.Controls 
import QtQuick.Layouts

GroupBox {    
    id: control  

    property bool reloadable: false    

    signal reloadContent()

    background: Rectangle {
        y: control.topPadding - control.bottomPadding
        radius: 5
        color: "#cce"
        width: parent.width
        height: parent.height - control.topPadding + control.bottomPadding
        border.color: "#888"                       
    }

    label: RowLayout {
        x: control.leftPadding
        height: lbl.height
        spacing: 10

        Label {       
            id: lbl     
            text: control.title 
            color: "black"
            elide: Text.ElideRight        
        }
        BoutonReload {       
            visible: reloadable

            MouseArea {
                anchors.fill: parent

                Connections {
                    function onClicked() {
                        control.reloadContent()
                    }
                }
            }
        } 
    }
}
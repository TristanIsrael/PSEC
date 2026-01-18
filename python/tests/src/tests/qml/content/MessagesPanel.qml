import QtQuick
import Components
import PSEC

PanelBase {
    id: root

    implicitWidth: Environment.mainWidth * 0.5
    implicitHeight: Environment.mainHeight * 0.1

    Item {
        id: wrapper
        anchors.fill: parent
        clip: true

        readonly property int lines: 3

        ListView {
            id: listView

            anchors {
                fill: parent
                margins: parent.height * 0.05
            }

            model: bindings.messagesModel

            onCountChanged: {
                const txt = itemAtIndex(count -1)
                listView.positionViewAtIndex(count-1, ListView.Contain)
                /*console.debug(txt.y, listView.height, txt.text, count)
                if(txt !== null && txt.y > listView.height) {
                    listView.contentY = txt.y - listView.height + txt.height
                }*/
            }

            delegate: Text {
                text: datetime +" - " +label
                font.pixelSize: 18
                color: {
                    switch(criticity) {
                        case Enums.MessageLevel.Warning: return Environment.colorWarning
                        case Enums.MessageLevel.Error: return Environment.colorError
                        case Enums.MessageLevel.User: return Environment.colorUserMessage
                        default: Environment.colorText
                    }
                }                
            }

            Behavior on contentY {
                PropertyAnimation {
                    id: animateScroll
                    duration: 200
                }
            }

        }
    }

    Bindings {
        id: bindings
    }
}

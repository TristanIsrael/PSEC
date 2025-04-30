import QtQuick

Image {
    id: root

    property string type
    width: 16
    height: 16

    source: root.type === "file" ? Qt.resolvedUrl("images/file.png") : root.type === "special_up" ? Qt.resolvedUrl("images/folder_up.png") : Qt.resolvedUrl("images/folder.png")
}
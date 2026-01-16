import QtQuick
import QtQuick.Layouts
import Components

Item {
    width: implicitWidth
    height: implicitHeight
    implicitWidth: 600
    implicitHeight: 800

    ColumnLayout {
        anchors.fill: parent
        spacing: 20

        ListView {
            id: root

            Layout.fillWidth: true
            Layout.fillHeight: true

            model: bindings.testsListModel

            delegate: ProgressListEntry {
                implicitWidth: parent.width

                label: display
                progress: RoleProgress
            }
        }
    }

    Bindings {
        id: bindings
    }
}

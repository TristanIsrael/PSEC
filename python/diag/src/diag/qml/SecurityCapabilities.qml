import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Components
import net.alefbet

ColumnLayout {
    id: root

    property var cpuInfo: AppController.cpuInfo
    property var cpuFlags: cpuInfo["flags"]

    spacing: 20

    PText {
        text: qsTr("Security capabilities")
        color: Colors.cyan
        font.pixelSize: 16
        font.bold: true
    }    

    PCapability {
        text: qsTr("IOMMU")
        state: AppController.hasVTd ? qsTr("OK") : qsTr("KO")
        stateColor: AppController.hasVTd ? Colors.green : Colors.red
    }
    
    PCapability {
        text: qsTr("Page tables")
        state: cpuFlags["ept"] !== undefined ? qsTr("OK") : qsTr("KO")
        stateColor: cpuFlags["ept"] !== undefined ? Colors.green : Colors.yellow
    }

    PCapability {
        text: qsTr("HVM support")
        state: AppController.hasHVM ? qsTr("OK") : qsTr("KO")
        stateColor: AppController.hasHVM ? Colors.green : Colors.yellow
    }

    /*PCapability {
        text: qsTr("PVH support")
        state: qsTr("Unknown")
        stateColor: Colors.yellow
    }*/

    /*PCapability {
        text: qsTr("XSM Flask support")
        state: qsTr("Unknown")
        stateColor: Colors.yellow
    }*/

    Item {
        Layout.fillHeight: true
    }
}

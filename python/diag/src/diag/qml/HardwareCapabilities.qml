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
        text: qsTr("Hardware specifications")
        color: Colors.cyan
        font.pixelSize: 16
        font.bold: true
    }

    /*"count": 12,
        "arch_string_raw": "x86_64",
        "vendor_id_raw": "GenuineIntel",
        "brand_raw": "12th Gen Intel(R) Core(TM) i5-1230U",
        "hz_advertised_friendly": "1.6896 GHz",
        "hz_actual_friendly": "1.6896 GHz"
    */

    PCapability {
        text: qsTr("CPU Cores")
        state: cpuInfo["count"] < 2 ? qsTr("KO") : cpuInfo["count"] >= 4 ? qsTr("OK") : qsTr("Passable")
        stateColor: cpuInfo["count"] < 2 ? Colors.red : cpuInfo["count"] >= 4 ? Colors.green : Colors.yellow
        stateDescription: qsTr("Core count : %1").arg(cpuInfo["count"])
    }

    PCapability {
        text: qsTr("CPU architecture")
        state: cpuInfo["arch_string_raw"] +" " +cpuInfo["bits"] +"bit"
        stateColor: cpuInfo["arch_string_raw"] === "x86_64" ? Colors.green : Colors.red
    }

    PCapability {
        text: qsTr("CPU vendor")
        state: cpuInfo["vendor_id_raw"]
    }

    PCapability {
        text: qsTr("CPU model")
        state: cpuInfo["brand_raw"]
    }

    PCapability {
        text: qsTr("CPU frequency")
        state: cpuInfo["hz_actual_friendly"]
    }    

    PCapability {
        text: qsTr("VT-x")
        state: flags["vmx"] !== undefined ? qsTr("OK") : qsTr("KO")
        stateColor: flags["vmx"] !== undefined ? Colors.green : Colors.red
    }

    PCapability {
        text: qsTr("RAM")
        state: AppController.installedMemory >= 4 ? qsTr("OK") : AppController.installedMemory >= 2 ? qsTr("Passable") : "KO"
        stateColor: AppController.installedMemory >= 4 ? Colors.green : AppController.installedMemory >= 2 ? Colors.yellow : Colors.red
        stateDescription: qsTr("Installed memory: %1 GB").arg(AppController.installedMemory)
    }

    Item {
        Layout.fillHeight: true
    }
}

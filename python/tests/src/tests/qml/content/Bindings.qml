import QtQuick
import Components
import PSEC

Item {
    id: root

    /* Bindings */
    property bool handheld: true
    property bool ready: true
    property bool running: false
    property int batteryLevel: 100
    property bool plugged: true
    property bool ambientLightSensorReady: false
    property int ambientLight: 0 // 0 (dark) - 100 (sunny)
    property int systemState: 0
    property int nbTestsTotal: 857
    property int nbTestsFailed: 123
    property int nbTestsSucceeded: 543
    property int nbCapacitiesTotal: 12
    property int nbCapacitiesFailed: 0
    property int nbCapacitiesSucceeded: 11

    /* Models */
    property var testsListModel: modelTest

    /* System states */
    readonly property color systemStateColor: {
        if(!bindings.ready) {
            return Environment.colorFilterNotReady
        } else {
            if(bindings.infected) {
                return Environment.colorFilterInfected
            } else if(bindings.used) {
                return Environment.colorFilterUsed
            }
        }

        return Environment.colorFilterReady
    }

    /* Functions */


    /**
        For development only
    */
    ListModel {
        id: debugMessages
    }

    ListModel {
            id: modelTest
            ListElement {
                display: "Capacité 1"
                RoleProgress: 20
                RoleSuccess: false
            }

            ListElement {
                display: "Un premier test pour voir"
                RoleProgress: 100
                RoleSuccess: true
            }

            ListElement {
                display: "Test bidule pour le machin"
                RoleProgress: 96
            }
        }


}

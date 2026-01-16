import QtQuick
import QtQuick.Layouts
import Components

GridLayout {
    id: lytResults

    width: implicitWidth
    height: implicitHeight
    implicitWidth: 400
    implicitHeight: 100

    rows: 2
    columns: 3
    columnSpacing: 20
    rowSpacing: 10

    StyledText {
        text: qsTr("Capacities: %1").arg(bindings.nbCapacitiesTotal)
    }

    StyledText {
        text: qsTr("Succeeded: %1").arg(bindings.nbCapacitiesSucceeded)
    }

    StyledText {
        text: qsTr("Failed: %1").arg(bindings.nbCapacitiesFailed)
    }

    StyledText {
        text: qsTr("Tests: %1").arg(bindings.nbTestsTotal)
    }

    StyledText {
        text: qsTr("Succeeded: %1").arg(bindings.nbTestsSucceeded)
    }

    StyledText {
        text: qsTr("Failed: %1").arg(bindings.nbTestsFailed)
    }

    Bindings {
        id: bindings
    }
}

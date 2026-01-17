import QtQuick

TopBarUi {
    id: root

    /* Composition */ 
    gradientStart.color: Qt.alpha(bindings.systemStateColor, 0.0)
    gradientStop.color: Qt.alpha(bindings.systemStateColor, 0.1)

    Timer {
        triggeredOnStart: true
        interval: 1000
        running: true
        repeat: true
        onTriggered: updateTime()
    }

    /* Slots */
    Connections {
        target: maHour
        function onClicked() {
            updateTime()
        }
    }

    Component.onCompleted: function() {
        updateTime()
    }

    // Functions
    function updateTime() {
        const now = new Date()
        const localTime = Qt.formatTime(new Date(), "HH:mm:ss");
        lblTime.text = localTime
    }

    Bindings {
        id: bindings
    }

}

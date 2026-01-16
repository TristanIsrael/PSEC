import QtQuick

TopBarUi {
    id: root

    property bool timeFormatZulu: true

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
            timeFormatZulu = !timeFormatZulu
            updateTime()
        }
    }

    Component.onCompleted: function() {
        updateTime()
    }

    // Functions
    function updateTime() {
        //Conversion en TZ Zulu
        const now = new Date()
        const zulu = new Date(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDay(), now.getUTCHours(), now.getUTCMinutes(), now.getUTCSeconds())
        const localTime = Qt.formatTime(new Date(), "HH:mm:ss");
        const zuluTime = Qt.formatTime(zulu, "HH:mm:ssZ");
        lblTime.text = timeFormatZulu ? zuluTime : localTime
    }

    Bindings {
        id: bindings
    }

}

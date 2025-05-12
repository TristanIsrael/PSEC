import QtQuick
import net.alefbet

MainScreenUi {
    id: root    

    btnDemarrer.enabled: AppController.ready && fldMessage.text !== ""
    fldMessage.readOnly: !AppController.ready
    fldResult.text: AppController.result
}
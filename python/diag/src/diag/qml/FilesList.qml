import QtQuick
import net.alefbet

FilesListUi {
    id: root

    property string selectedDisk

    listView.model : DiskProxyModel {
        id: listViewModel
        source: DiskModel
        disk: root.selectedDisk
    }

    onSelectedDiskChanged: function() {
        console.debug("Update files list for", root.selectedDisk)
        root.selectedFile = ""
    }

    onItemClicked: function(row) {
        if (fileType === "special_up") {
            AppController.debug("Up")
            lv.model.go_up()
            selectedFile = ""
        } else if (fileType === "folder") {
            AppController.debug("Afficher %1".arg(
                                    lblFilename.text))
            lv.model.folder = lblFilename.text
            currentFolder = lv.model.folder
            selectedFile = ""
        } else if (fileType === "file") {
            selectedFile = lblFilename.text
        }
    }
    
}

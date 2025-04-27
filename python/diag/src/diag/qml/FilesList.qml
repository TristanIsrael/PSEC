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

    onSelectedFileChanged: function() {
        InterfaceSocle.get_disk_content(root.selectedDisk, root.selectedFile)
    }

    onItemClicked: function(row, fileType, path, fileName) {
        console.debug(fileType)

        if (fileType === "special_up") {
            AppController.debug("Up")
            listViewModel.go_up()
            selectedFile = ""
        } else if (fileType === "folder") {       
            //const filePath = "%1/%2".arg(path === "/" ? "" : path).arg(fileName)     
            AppController.debug("Dossier sélectionné: %1".arg(fileName))
            listViewModel.folder = fileName
            //currentFolder = listViewModel.folder
            selectedFile = ""
        } else if (fileType === "file") {
            AppController.debug("Fichier sélectionné: %1".arg(fileName))
            selectedFile = fileName
        }
    }   
    
}

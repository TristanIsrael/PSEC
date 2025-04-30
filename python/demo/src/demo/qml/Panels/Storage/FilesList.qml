import QtQuick
import net.alefbet

FilesListUi {
    id: root

    property string selectedDisk
    property string currentDir: "/"

    listView.model : DiskModel

    onSelectedDiskChanged: function() {
        root.selectedFile = ""
    }

    onItemClicked: function(row, type, path, fileName) {
        //console.debug("Item selected", type, path, fileName)

        if (type === "special_up") {
            root.currentDir = get_parent_dir(root.currentDir)
            root.selectedFile = ""
            InterfaceSocle.get_disk_content(root.selectedDisk, root.currentDir)
        } else if (type === "folder") {       
            root.currentDir = path + (path.endsWith("/") ? "" : "/") + fileName
            InterfaceSocle.get_disk_content(root.selectedDisk, root.currentDir)
            selectedFile = ""
        } else if (type === "file") {
            selectedFile = fileName
        }
    }   

    function get_parent_dir(dir) {
        return dir.substring(0, dir.lastIndexOf("/"))
    }
    
}

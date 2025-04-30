import QtQuick
import net.alefbet

PanneauDepotUi {
    id: root

    /**
        Slots
     */
    Connections {
        target: InterfaceSocle
        function onBenchmarkDataChanged() {
            //Metrics are:
            //- write_on_disk
            //- read_from_disk
            //- copy_to_repository                        

            debitEcritureUSB10Ko = compute_bandwidth("write_usb_10k", 10)
            debitLectureUSB10Ko = compute_bandwidth("read_usb_10k", 10)
            debitEcritureDepot10Ko = compute_bandwidth("copy_repository_10k", 10)
          
            debitEcritureUSB100Ko = compute_bandwidth("write_usb_100k", 100)
            debitLectureUSB100Ko = compute_bandwidth("read_usb_100k", 100)
            debitEcritureDepot100Ko = compute_bandwidth("copy_repository_100k", 100)

            debitEcritureUSB500Ko = compute_bandwidth("write_usb_500k", 500)
            debitLectureUSB500Ko = compute_bandwidth("read_usb_500k", 500)
            debitEcritureDepot500Ko = compute_bandwidth("copy_repository_500k", 500)

            debitEcritureUSB1Mo = compute_bandwidth("write_usb_1m", 1*1024)
            debitLectureUSB1Mo = compute_bandwidth("read_usb_1m", 1*1024)
            debitEcritureDepot1Mo = compute_bandwidth("copy_repository_1m", 1*1024)

            debitEcritureUSB10Mo = compute_bandwidth("write_usb_10m", 10*1024)
            debitLectureUSB10Mo = compute_bandwidth("read_usb_10m", 10*1024)
            debitEcritureDepot10Mo = compute_bandwidth("copy_repository_10m", 10*1024)

            debitEcritureUSB100Mo = compute_bandwidth("write_usb_100m", 100*1024)
            debitLectureUSB100Mo = compute_bandwidth("read_usb_100m", 100*1024)
            debitEcritureDepot100Mo = compute_bandwidth("copy_repository_100m", 100*1024)
        }
    }

    Connections {
        target: btnStartBenchmark
        function onClicked() {
            AppController.start_benchmark_files()
        }
    }

    Connections {
        target: grpDepot
        function onReloadContent() {
            AppController.debug("L'utilisateur demande le rafraichissement du dépôt")
            InterfaceSocle.get_contenu_depot()
        }
    }

    Component.onCompleted: function() {
        AppController.debug("Demande le contenu du dépôt")
        InterfaceSocle.get_contenu_depot()
    }

    /**
        Fonctions
     */
    function compute_bandwidth(dict_entry_name, size_ko) {
        const dict_entry = InterfaceSocle.benchmarkData[dict_entry_name]
        var iterations = dict_entry["iterations"]
        var total_duration_ms = dict_entry["total_duration"]
        var total_duration_s = 0.0
        var total_size_mo = 0.0
        var bandwidth = 0.0

        if(iterations !== undefined && total_duration_ms !== undefined) {
            total_duration_s = total_duration_ms/1000.0
            total_size_mo = iterations * (size_ko/1024)
            bandwidth = total_size_mo/total_duration_s
            AppController.debug("débit", dict_entry_name, bandwidth)                      
        }

        return bandwidth
    }

}
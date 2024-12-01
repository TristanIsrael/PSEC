import QtQuick
import net.alefbet

PanneauInputsUi {

    Connections {
        target: swMousePosition
        function onPositionChanged() {
            AppController.followMouseCursor = (swMousePosition.position > 0)
        }
    }

    Connections {
        target: btnStartBenchmark
        function onClicked() {
            AppController.info(qsTr("L'utilisateur demande le démarrage du benchmark inputs"))
            AppController.start_benchmark_inputs()
        }
    }

    Connections {
        target: InterfaceSocle
        function onBenchmarkDataChanged() {
            AppController.info(qsTr("Données de benchmark reçues"))
            var benchmarkData = InterfaceSocle.benchmarkData
            if(benchmarkData !== undefined) {
                if(benchmarkData["inputs_duration"] !== undefined) 
                    dureeEmission = benchmarkData["inputs_duration"]
                if(benchmarkData["inputs_iterations"] !== undefined)
                    iterationsEmises = benchmarkData["inputs_iterations"]
                if(dureeEmission > 0)                
                    debitGeneral = (iterationsEmises*100)/dureeEmission
            }
        }
       
    }

}
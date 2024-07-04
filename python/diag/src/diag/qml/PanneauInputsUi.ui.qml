import QtQuick
import QtQuick.Controls 
import QtQuick.Layouts
import net.alefbet

RowLayout {
    property int dureeEmission: 0
    property int dureeReception: 0
    property int iterationsEmises: 0
    property int iterationsRecues: 0
    property int debitGeneral: 0
    property int debitCourant: 0

    property alias swMousePosition: swMousePosition    
    property alias btnStartBenchmark: btnStartBenchmark
    
    spacing: 10
    //implicitHeight: grpEntrees.height+spacing+grpBenchmark.height

    Group {    
        title: qsTr("Entrées")   
        id: grpEntrees
        Layout.preferredHeight: Math.max(grpBenchmark.implicitHeight, implicitHeight)
        Layout.preferredWidth: parent.width - grpBenchmark.width - parent.spacing

        RowLayout {
            anchors.fill: parent
            spacing: 20

            GridLayout {
                id: lyt
                columns: 2
                uniformCellHeights: true
                height: parent.height
                
                //1:1
                Text { text: qsTr("Position du pointeur :") }
                //1:2
                RowLayout { 
                    RectangleValeur { text: "%1,%2".arg(AppController.mouseX).arg(AppController.mouseY) } 
                    Switch { id: swMousePosition; text: qsTr("Activer") }
                }
            
                //2:1
                Text { text: qsTr("Position du clic/toucher :") }
                //2:2
                RectangleValeur { text: "%1,%2".arg(AppController.clicX).arg(AppController.clicY) }   

                //3:1        
                Text { text: qsTr("Action de la molette :") }
                //3:2
                Text {
                    id: lblMolette
                    text: qsTr("direction : %1").arg(AppController.wheel === 1 ? "haut" : AppController.wheel === -1 ? "bas" : "aucune")
                }

                Item {
                    Layout.fillHeight: true
                }
            }

            ColumnLayout {
                Text { 
                    text: qsTr("Tests manuels") 
                    font.bold: true
                }  

                RowLayout {                      
                    ComboBox {
                        id: cbTestSouris                    
                        model: [
                            "Element 1",
                            "Element 2",
                            "Element 3"
                        ]

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            propagateComposedEvents: true
                            visible: true

                            Connections {
                                function onEntered() {
                                    lblTestManuel.text = qsTr("Combobox survolée")
                                }
                                function onExited() {
                                    lblTestManuel.text = qsTr("Combobox non survolée")
                                }
                                /*onClicked: function(mouse) {
                                    lblTestManuel.text = qsTr("Combobox cliquée")
                                }*/
                            }
                        }
                    }     

                    Slider {
                        id: sldTest
                        from: 0
                        to: 100
                        stepSize: 1

                        onValueChanged: function() {
                            lblTestManuel.text = qsTr("Valeur : %1").arg(value)
                        }
                    }  
                }

                Text {
                    id: lblTestManuel
                    text: qsTr("Combobox non survolée")
                }

                RowLayout {
                    width: parent.width

                    TextField {
                        id: txtEdit
                        Layout.preferredWidth: parent.width
                        placeholderText: qsTr("Saisie clavier")
                    } 
                }   

                Item {
                    Layout.fillHeight: true
                }         
            }
        }
    }

    Group {    
        id: grpBenchmark
        title: qsTr("Benchmark")    
        Layout.preferredHeight: Math.max(grpEntrees.implicitHeight, implicitHeight)

        GridLayout {     
            columns: 2

            Button {
                id: btnStartBenchmark
                Layout.columnSpan: 2
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("Démarrer")
            }                

            Text {
                horizontalAlignment: Text.AlignRight
                font.bold: true
                text: qsTr("Durée émission")
            }

            Text {
                text: "%1 ms".arg(dureeEmission)
            } 

            Text {
                horizontalAlignment: Text.AlignRight
                font.bold: true
                text: qsTr("Durée réception")
            }

            Text {
                text: "%1 ms".arg(dureeReception)
            }

            Text {
                horizontalAlignment: Text.AlignRight
                font.bold: true
                text: qsTr("Itérations émises")
            }

            Text {
                text: "%1".arg(iterationsEmises)
            }

            Text {
                horizontalAlignment: Text.AlignRight
                font.bold: true
                text: qsTr("Itérations reçues")
            }

            Text {
                text: "%1".arg(iterationsRecues)
            }

            Text {
                horizontalAlignment: Text.AlignRight
                font.bold: true
                text: qsTr("Débit général")
            }

            Text {
                text: "%1/cs".arg(debitGeneral)
            }

            Text {
                horizontalAlignment: Text.AlignRight
                font.bold: true
                text: qsTr("Débit courant")
            }

            Text {
                text: "%1/cs".arg(debitCourant)
            }            
        }
    }
}
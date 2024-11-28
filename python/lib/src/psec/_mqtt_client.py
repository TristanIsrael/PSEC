import os, time, serial, json, threading
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion

class ConnectionType():
    UNIX_SOCKET = "unix_socket"
    SERIAL_PORT = "serial_port"
    TCP_DEBUG = "tcp"

class SerialTransport:
    def __init__(self, port, baudrate=115200):
        self.serial = serial.Serial(port, baudrate)

    def write(self, data):
        """Envoyer des données sur le port série."""
        self.serial.write(data)

    def read(self):
        """Lire des données du port série."""
        if self.serial.in_waiting > 0:
            return self.serial.read(self.serial.in_waiting)
        return b""
    
class SerialMQTTClient(mqtt.Client):
    def __init__(self, serial_transport, *args, **kwargs):
        super().__init__(callback_api_version=CallbackAPIVersion.VERSION2, *args, **kwargs)
        self.serial_transport = serial_transport

    def _send_packet(self, packet):
        """Remplacer l'envoi de paquets MQTT pour utiliser le port série."""
        self.serial_transport.write(packet)

    def _packet_read(self):
        """Lire les données reçues via le port série."""
        return self.serial_transport.read()

class MqttClient():
    connection_type:ConnectionType = ConnectionType.UNIX_SOCKET
    connection_string:str = ""
    identifier:str = "unknown"
    on_connected = None
    on_message = None

    def __init__(self, identifier:str, connection_type:ConnectionType = ConnectionType.UNIX_SOCKET, connection_string:str = ""):
        self.identifier = identifier
        self.connection_type = connection_type
        self.connection_string = connection_string

    def __del__(self):
        self.stop()   

    def start(self):        
        print("Starting MQTT client {}".format(self.identifier))

        if self.connection_type != ConnectionType.SERIAL_PORT:            
            self.mqtt_client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, client_id=self.identifier, transport=self.__get_transport_type())
            self.mqtt_client.on_connect = self.__on_connected
            self.mqtt_client.on_message = self.__on_message
            
            if self.connection_type == ConnectionType.TCP_DEBUG:
                self.mqtt_client.connect("localhost")
            elif self.connection_type == ConnectionType.UNIX_SOCKET:
                self.mqtt_client.connect("localhost", unix_socket_path=self.connection_string)
            else:
                print("The connection type {} is not handled".format(self.connection_type))
                return
        elif self.connection_type == ConnectionType.SERIAL_PORT:            
            serial_transport = SerialTransport(port=self.connection_string, baudrate=115200)
            self.mqtt_client = SerialMQTTClient(serial_transport)
            self.mqtt_client.on_connect = self.__on_connected
            self.mqtt_client.on_message = self.__on_message
            self.mqtt_client.connect("localhost")
        else:
            print("The connection type {} is not handled".format(self.connection_type))
            return
        
        self.mqtt_client.loop_start()

    def stop(self):
        if self.mqtt_client is not None:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            print("Mqtt client exited")

    #def subscribe(self, topic:str):
    #   print("Subscribe to topic {}".format(topic))
    #    self.mqtt_client.subscribe(topic)

    def subscribe(self, topics:list):
        for topic in topics:
            self.mqtt_client.subscribe(topic)

    def publish(self, topic:str, payload:dict):
        self.mqtt_client.publish(topic, json.dumps(payload))

    def __get_transport_type(self):
        if self.connection_type == ConnectionType.TCP_DEBUG:
            return "tcp"
        elif self.connection_type == ConnectionType.UNIX_SOCKET:
            return "websockets"
        
        return "" 
    
    def __on_message(self, client, userdata, msg):
        #print(f"[{userdata}] Message reçu sur {msg.topic}: {msg.payload.decode()}")
        if self.on_message is not None:
            payload = json.loads(msg.payload.decode())
            self.on_message(msg.topic, payload)
        else:
            print("No message callback")

    def __on_connected(self, client, userdata, connect_flags, reason_code, properties):
        print("Connected to the MQTT broker")
        if self.on_connected is not None:
            self.on_connected()
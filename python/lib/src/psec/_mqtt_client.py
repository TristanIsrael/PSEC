import os, time, serial, json, threading
import paho.mqtt.client as mqtt
from paho.mqtt import client
from paho.mqtt.client import CallbackAPIVersion

class ConnectionType():
    UNIX_SOCKET = "unix_socket"
    SERIAL_PORT = "serial_port"
    TCP_DEBUG = "tcp"

class SerialSocket():
    def __init__(self, path:str, baudrate:int):
        #print("Connect to serial port")
        self.serial = serial.Serial(path, baudrate)

    def recv(self, buffer_size: int) -> bytes:
        if self.serial.in_waiting > 0:
            return self.serial.read(buffer_size)
        
        return b""   
    
    def send(self, buffer: bytes) -> int:
        #print("Write data on serial port")
        return self.serial.write(buffer)

    def close(self) -> None:
        #print("Close serial port")
        self.serial.close()

    def fileno(self) -> int:
        return self.serial.fileno()

    def setblocking(self, flag: bool) -> None:
        pass
    
class SerialMQTTClient(mqtt.Client):
    def __init__(self, path:str, baudrate:int, *args, **kwargs):
        super().__init__(callback_api_version=CallbackAPIVersion.VERSION2, *args, **kwargs)
        self.path = path
        self.baudrate = baudrate

    def _create_socket(self):
        try:
            socket = SerialSocket(self.path, self.baudrate)
            self._sockpairR = socket
            #print("Socket created")
            return socket
        except:
            print("An error occured while opening the serial port")
            return None

class MqttClient():
    connection_type:ConnectionType = ConnectionType.UNIX_SOCKET
    connection_string:str = ""
    identifier:str = "unknown"
    on_connected = None
    on_message = None
    connected = False
    is_starting = False
    can_run = True

    def __init__(self, identifier:str, connection_type:ConnectionType = ConnectionType.UNIX_SOCKET, connection_string:str = ""):
        self.identifier = identifier
        self.connection_type = connection_type
        self.connection_string = connection_string

    def __del__(self):
        self.stop()   

    def start(self):        
        if self.is_starting or self.connected:
            return
        
        self.is_starting = True
        self.can_run = True
        print("Starting MQTT client {}".format(self.identifier))        

        if self.connection_type != ConnectionType.SERIAL_PORT:            
            self.mqtt_client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, client_id=self.identifier, transport=self.__get_transport_type(), reconnect_on_failure=True)
            self.mqtt_client.on_connect = self.__on_connected
            self.mqtt_client.on_message = self.__on_message
            
            if self.connection_type == ConnectionType.TCP_DEBUG:
                self.mqtt_client.connect(host="localhost")
            elif self.connection_type == ConnectionType.UNIX_SOCKET:
                self.mqtt_client.connect(host=self.connection_string, port=1)
            else:
                print("The connection type {} is not handled".format(self.connection_type))
                return
            
            self.mqtt_client.loop_start()
        elif self.connection_type == ConnectionType.SERIAL_PORT:            
            #serial_transport = SerialTransport(port=self.connection_string, baudrate=115200)
            self.mqtt_client = SerialMQTTClient(path=self.connection_string, baudrate=115200, reconnect_on_failure=True)
            self.mqtt_client.on_connect = self.__on_connected
            self.mqtt_client.on_message = self.__on_message
            self.mqtt_client.connect(host="localhost", port=1)

            threading.Thread(target=self.mqtt_client.loop_forever).start()
        else:
            print("The connection type {} is not handled".format(self.connection_type))
            return        

    def stop(self):
        if self.mqtt_client is not None:
            self.can_run = False
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
            return "unix"
        
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
        self.connected = True
        
        if self.on_connected is not None:
            self.on_connected()

        print("Starting keepalive")
        threading.Timer(30, self.__keepalive).start()

    def __keepalive(self):
        if self.connected and self.can_run:
            self.mqtt_client.publish("misc/keepalive", "ping")
            threading.Timer(30, self.__keepalive).start()

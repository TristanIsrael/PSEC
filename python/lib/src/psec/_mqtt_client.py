''' \author Tristan Israël
'''
from enum import StrEnum
import time
import json
import threading
import atexit
import select
from typing import Literal, Callable, Optional
import serial
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion, MQTTErrorCode

DEBUG = False
TYPE_CHECKING = True

class ConnectionType(StrEnum):
    ''' @brief Cette énumération permet d'identifier le type de connexion utilisée.
    '''
    UNIX_SOCKET = "unix_socket"
    SERIAL_PORT = "serial_port"
    TCP_DEBUG = "tcp"

class SerialSocket():
    ''' @brief Cette classe implémente une socket série.

    La socket série est utilisée pour communiquer sur un port série dans un DomU
    ou sur une socket de domaine UNIX sur le Dom0.
    '''

    def __init__(self, path:str, baudrate:int):
        print(f"Connect to serial port {path}")
        self.serial = serial.Serial(port=path, baudrate=baudrate, timeout=0, write_timeout=0)
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()


    def recv(self, buffer_size: int) -> bytes:
        #print("wait for bytes")
        if self.serial is not None and self.serial.is_open:
            data = self.serial.read(buffer_size)
            return data

        return b""

    def send(self, buffer: bytes) -> int:
        if self.serial is not None and self.serial.is_open:
            #print("send:{}".format(buffer))
            sent = self.serial.write(buffer)
            return sent if sent is not None else 0
        
        return 0

    def close(self) -> None:
        print("Close serial port")
        if self.serial is not None and self.serial.is_open:
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            self.serial.close()

    def fileno(self) -> int:
        return self.serial.fileno()

    def setblocking(self, flag: bool) -> None:
        pass


class SerialMQTTClient(mqtt.Client):
    ''' @brief Cette classe permet au client MQTT de communiquer sur un port série.
    '''

    def __init__(self, path:str, baudrate:int, *args, **kwargs):
        super().__init__(callback_api_version=CallbackAPIVersion.VERSION2, *args, **kwargs)
        self.path = path
        self.baudrate = baudrate
        self.sock_ = None

    def close(self):
        if self.sock_ is not None:
            self.sock_.close()

    def loop_start(self) -> MQTTErrorCode:
        self._thread_terminate = False
        self._thread = threading.Thread(target=self.__do_loop)
        self._thread.daemon = True
        self._thread.start()

        return MQTTErrorCode.MQTT_ERR_SUCCESS

    def __do_loop(self):
        rc = MQTTErrorCode.MQTT_ERR_SUCCESS

        while not self._thread_terminate:
            rlist, wlist, _ = select.select([self.sock_], [self.sock_], [], 1)

            if rlist:
                rc = self.loop_read()
                if rc != MQTTErrorCode.MQTT_ERR_SUCCESS:
                    print(f"Read error {rc}")
                    break

            if self.want_write() and wlist:
                rc = self.loop_write()
                if rc != MQTTErrorCode.MQTT_ERR_SUCCESS:
                    print(f"Write error {rc}")
                    break

            rc = self.loop_misc()
            if rc != MQTTErrorCode.MQTT_ERR_SUCCESS:
                print(f"Misc error {rc}")
                break

            time.sleep(0.2)

        print("MQTT loop ended")

    def loop_stop(self) -> MQTTErrorCode:
        self._thread_terminate = True

        if self._thread is not None:
            self._thread.join()
            return MQTTErrorCode.MQTT_ERR_SUCCESS

        return MQTTErrorCode.MQTT_ERR_UNKNOWN

    def _create_socket(self):
        try:
            print(f"Create socket on {self.path}")
            self.sock_ = SerialSocket(self.path, self.baudrate)
            self._sockpairR = self.sock_
            return self.sock_
        except Exception as e:
            print("An error occured while opening the serial port")
            print(e)
            return None

class MqttClient():
    ''' @brief Cette classe permet d'échanger des messages MQTT au sein du système.
    '''

    connection_type:ConnectionType = ConnectionType.UNIX_SOCKET
    connection_string:str = ""
    identifier:str = "unknown"
    on_connected: Optional[Callable[[], None]] = None
    on_message: Optional[Callable[[str, dict], None]] = None
    __message_callbacks = []
    __connected_callbacks = []
    connected = False
    is_starting = False

    def __init__(self, identifier:str, connection_type:ConnectionType = ConnectionType.UNIX_SOCKET, connection_string:str = ""):
        self.mqtt_client = None
        self.identifier = identifier
        self.connection_type = connection_type
        self.connection_string = connection_string
        atexit.register(self.stop)

    def __del__(self):
        self.stop()

    def start(self):
        if self.is_starting or self.connected:
            return
        
        self.is_starting = True
        print(f"Starting MQTT client {self.identifier}")

        if self.connection_type != ConnectionType.SERIAL_PORT:
            self.mqtt_client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, client_id=self.identifier, transport=self.__get_transport_type(), reconnect_on_failure=True)
            self.mqtt_client.on_connect = self.__on_connected
            self.mqtt_client.on_message = self.__on_message

            mqtt_host = "undefined"
            try:
                if self.connection_type == ConnectionType.TCP_DEBUG:
                    mqtt_host = "localhost"
                    self.mqtt_client.connect(host=mqtt_host, keepalive=30)
                elif self.connection_type == ConnectionType.UNIX_SOCKET:
                    mqtt_host = self.connection_string
                    self.mqtt_client.connect(host=mqtt_host, port=1, keepalive=30)
                else:
                    print(f"The connection type {self.connection_type} is not handled")
                    return
            except Exception as e:
                print(f"Could not connect to the MQTT broker on {mqtt_host}")
                print(e)
                return
            
            self.mqtt_client.loop_start()
        elif self.connection_type == ConnectionType.SERIAL_PORT:
            self.mqtt_client = SerialMQTTClient(client_id=self.identifier, path=self.connection_string, baudrate=115200, reconnect_on_failure=False)
            self.mqtt_client.on_connect = self.__on_connected
            self.mqtt_client.on_message = self.__on_message
            self.mqtt_client.on_disconnect = self.mqtt_client.close

            if DEBUG:
                self.mqtt_client.on_log = self.__on_log
            self.mqtt_client.connect(host="localhost", port=1, keepalive=30)

            #threading.Thread(target=self.mqtt_client.loop_forever).start()
            self.mqtt_client.loop_start()
        else:
            print(f"The connection type {self.connection_type} is not handled")
            return

    def add_connected_callback(self, callback):
        self.__connected_callbacks.append(callback)

    def add_message_callback(self, callback):
        self.__message_callbacks.append(callback)

    def stop(self):
        if self.mqtt_client is not None:
            print("Quit Mqtt client")
            try:
                self.mqtt_client.disconnect()
                self.mqtt_client.loop_stop()
                if self.connection_type == ConnectionType.SERIAL_PORT:
                    self.mqtt_client.close()
            except:
                #Ignore exceptions when closing
                pass
            finally:
                self.connected = False
                self.is_starting = False

    def subscribe(self, topic:str):
        print(f"Subscribe to topic {topic}")
        self.mqtt_client.subscribe(topic)

    def publish(self, topic:str, payload:dict):
        self.mqtt_client.publish(topic=topic, payload=json.dumps(payload))

    def __get_transport_type(self) -> Literal['tcp', 'unix']:
        if self.connection_type == ConnectionType.TCP_DEBUG:
            return "tcp"
        else:
            return "unix"

    def __on_log(self, client, userdata, level, buf):
        print(f"[MQTT log]: {buf}")

    def __on_message(self, client:mqtt.Client, userdata, msg:mqtt.MQTTMessage):
        #print(f"[{userdata}] Message reçu sur {msg.topic}: {msg.payload.decode()}")        
        try:
            payload = json.loads(msg.payload.decode())
            if self.on_message is not None:
                self.on_message(msg.topic, payload)

            for cb in self.__message_callbacks:
                cb(msg.topic, payload)
        except Exception as e:
            print("[MQTT Client] Uncaught Exception when handling message:")
            print(f"Topic : {msg.topic}")
            print(f"Payload : {msg.payload}")
            print(f"Exception : {e}")
            print("** Notice that the error may come from the client callback **")

    def __on_connected(self, client:mqtt.Client, userdata, connect_flags, reason_code, properties):
        print("Connected to the MQTT broker")
        self.connected = True
        self.is_starting = False
        
        if self.on_connected is not None:
            self.on_connected()

        for cb in self.__connected_callbacks:
            cb()

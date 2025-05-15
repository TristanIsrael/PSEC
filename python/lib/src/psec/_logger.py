from . import MqttClient, SingletonMeta, Topics, MqttHelper, RequestFactory
import os
import zlib
import base64
import logging
import platform
from datetime import datetime

class FileHandler:
    def __init__(self, file_path, mode='w'):
        self.file_path = file_path
        self.mode = mode
        self.file = open(self.file_path, self.mode)
        print(f"File {self.file_path} opened in {self.mode} mode.")

    def __del__(self):
        if self.file and not self.file.closed:
            self.file.close()
            Logger().debug(f"File {self.file_path} closed.")

    def write(self, data):
        if 'w' in self.mode or 'a' in self.mode and self.file is not None:
            self.file.write(data)
        else:
            Logger().error("File not opened in write mode.")

    def flush(self):
        if self.file is not None:
            self.file.flush()

    def read(self):
        if 'r' in self.mode and self.file is not None:
            return self.file.read()
        else:
            Logger().error("File not opened in read mode.")

class Logger(metaclass=SingletonMeta):
    __is_setup = False
    __is_recording = False
    __log_level = logging.INFO
    __logfile = None

    def setup(self, module_name:str, mqtt_client:MqttClient, log_level:int = logging.INFO, recording:bool=False, filename:str="/var/log/psec.log"):
        if self.__is_setup:
            return
        
        self.__domain_name = platform.node()
        self.__module_name = module_name
        self.__mqtt_client = mqtt_client

        #self.__mqtt_client.add_connected_callback(self.__on_connected)
        self.__mqtt_client.add_message_callback(self.__on_message)

        self.__is_recording = recording
        self.__filename = filename

        # We open the log file
        if recording and self.__logfile is None:
            self.__open_log_file()
            self.__mqtt_client.subscribe(f"{Topics.EVENTS}/#")

        self.__is_setup = True

    def critical(self, description:str, module:str = ""):
        if not self.__is_setup:
            return
        payload = self.__create_event(module, description)
        self.__mqtt_client.publish("system/events/critical", payload)

    def error(self, description:str, module:str = ""):
        if not self.__is_setup:
            return
        payload = self.__create_event(module, description)
        self.__mqtt_client.publish("system/events/error", payload)

    def warning(self, description:str, module:str = ""):
        if not self.__is_setup:
            return
        payload = self.__create_event(module, description)
        self.__mqtt_client.publish("system/events/warning", payload)

    def warn(self, description:str, module:str = ""):
        if not self.__is_setup:
            return
        self.warning(description, module)

    def info(self, description:str, module:str = ""):
        if not self.__is_setup:
            return
        payload = self.__create_event(module, description)
        self.__mqtt_client.publish("system/events/info", payload)

    def debug(self, description:str, module:str = ""):
        if not self.__is_setup:
            return
        payload = self.__create_event(module, description)
        self.__mqtt_client.publish("system/events/debug", payload)

    @staticmethod
    def loglevel_from_topic(topic:str) -> int:
        if not topic.startswith("{}".format(Topics.EVENTS)):
            return
        
        if topic.endswith("debug"):
            return logging.DEBUG
        elif topic.endswith("info"):
            return logging.INFO
        elif topic.endswith("warning"):
            return logging.WARN
        elif topic.endswith("error"):
            return logging.ERROR
        elif topic.endswith("critical"):
            return logging.CRITICAL
        
        return logging.DEBUG    

    def __create_event(self, module:str, description:str) -> dict :
        if not self.__is_setup:
            return {}
        
        now = datetime.now()
        dt = now.strftime(f"%Y-%m-%d %H:%M:%S.{now.microsecond // 1000:03d}")

        payload = {
            "component": self.__domain_name,
            "module": module if module != "" else self.__module_name,
            "datetime": dt,
            "description": description
        }

        return payload    

    def __on_message(self, topic:str, payload:dict):
        if topic == Topics.SET_LOGLEVEL:
            self.__log_level = payload.get("level", "info")
        elif topic == Topics.SAVE_LOG and self.__is_recording:
            if not MqttHelper.check_payload(payload, ["disk", "filename"]):
                self.error("Missing required arguments: disk, filename")
                return
            
            disk = payload.get("disk", "")
            filename = payload.get("filename", "logfile.txt")
            # Prepend filename with a / if needed
            if not filename.startswith("/"):
                filename = "/"+filename
            
            self.info("Copying the log file to {}:{}".format(disk, filename))
            
            # Read all the data
            with open(self.__filename, "rb") as file:
                content = file.read()

            # Compress the data
            compressed_data = zlib.compress(content, level=1)  # 1-9

            # Create the file
            request = RequestFactory.create_request_create_file(filename, disk, base64.b64encode(compressed_data), True)
            self.__mqtt_client.publish("{}/request".format(Topics.CREATE_FILE), request)
             
        elif self.__is_recording:
            # Log message
            self.__write_log(topic, payload)

    def __write_log(self, topic:str, payload:dict):
        if not self.__is_recording or self.__logfile is None:
            return
        
        loglevel = "UNKNOWN"
        logtxt = ""

        # Extract the log level
        spl = topic.split("/")
        if len(spl) == 0:
            return        
        spl.reverse()
        loglevel = spl[0]

        if self.__log_level > self.__loglevel_value(loglevel):
            return

        # Craft the log text
        # Fields are: module, datetime, level, description
        logtxt = "[{}] [{}] {} - {}\n".format(payload.get("datetime"), loglevel, payload.get("module"), payload.get("description"))
        #print(logtxt)
        self.__logfile.write(logtxt)        
        self.__logfile.flush()
        
    def __open_log_file(self):
        self.__logfile = FileHandler(self.__filename, 'a')
        print(f"Le journal sera enregistré dans le fichier {self.__filename}")

    def __loglevel_value(self, level:str) -> int:
        if level == "debug":
            return logging.DEBUG
        elif level == "info":
            return logging.INFO
        elif level == "warn" or level == "warning":
            return logging.WARN
        elif level == "error":
            return logging.WARN
        elif level == "critical":
            return logging.CRITICAL
        
        return logging.NOTSET
    
    @staticmethod
    def format_logline(message:str) -> str:
        return f"{datetime.now():%Y-%m-%d %H:%M:%S} - {message}"
    
    @staticmethod
    def print(message:str) -> None:
        print(Logger.format_logline(message))

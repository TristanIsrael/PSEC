from . import MqttClient, SingletonMeta
import os
from datetime import datetime

class Logger(metaclass=SingletonMeta):
    is_setup = False

    def setup(self, module_name:str, mqtt_client:MqttClient):
        if self.is_setup:
            return
        
        self.domain_name = os.uname().nodename
        self.module_name = module_name
        self.mqtt_client = mqtt_client
        self.is_setup = True

    def critical(self, description:str, module:str = ""):
        payload = self.__create_event(module, description)
        self.mqtt_client.publish("system/events/critical", payload)

    def error(self, description:str, module:str = ""):
        payload = self.__create_event(module, description)
        self.mqtt_client.publish("system/events/error", payload)

    def warning(self, description:str, module:str = ""):
        payload = self.__create_event(module, description)
        self.mqtt_client.publish("system/events/warning", payload)

    def warn(self, description:str, module:str = ""):
        self.warning(description, module)

    def info(self, description:str, module:str = ""):
        payload = self.__create_event(module, description)
        self.mqtt_client.publish("system/events/info", payload)

    def debug(self, description:str, module:str = ""):
        payload = self.__create_event(module, description)
        self.mqtt_client.publish("system/events/debug", payload)

    def __create_event(self, module:str, description:str) -> dict :
        if not self.is_setup:
            print("Logger is not setup")
            return
        
        now = datetime.now()
        dt = now.strftime(f"%Y-%m-%d %H:%M:%S.{now.microsecond // 1000:03d}")

        payload = {
            "component": self.domain_name,
            "module": module if module != "" else self.module_name,
            "datetime": dt,
            "description": description
        }

        return payload
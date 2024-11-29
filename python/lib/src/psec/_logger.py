from . import MqttClient, SingletonMeta
import os
from datetime import datetime

class Logger(metaclass=SingletonMeta):

    def setup(self, module_name:str, client_log:MqttClient):
        self.domain_name = os.uname().nodename
        self.module_name = module_name
        self.client_log = client_log

        if not client_log.connected:
            self.client_log.start()

    def critical(self, description:str, module:str = ""):
        payload = self.__create_event(module, description)
        self.client_log.publish("system/events/critical", payload)

    def error(self, description:str, module:str = ""):
        payload = self.__create_event(module, description)
        self.client_log.publish("system/events/error", payload)

    def warning(self, description:str, module:str = ""):
        payload = self.__create_event(module, description)
        self.client_log.publish("system/events/warning", payload)

    def warn(self, description:str, module:str = ""):
        self.warning(description, module)

    def info(self, description:str, module:str = ""):
        payload = self.__create_event(module, description)
        self.client_log.publish("system/events/info", payload)

    def debug(self, description:str, module:str = ""):
        payload = self.__create_event(module, description)
        self.client_log.publish("system/events/debug", payload)

    def __create_event(self, module:str, description:str) -> dict :
        now = datetime.now()
        dt = now.strftime(f"%Y-%m-%d %H:%M:%S.{now.microsecond // 1000:03d}")

        payload = {
            "component": self.domain_name,
            "module": module if module is not "" else self.module_name,
            "datetime": dt,
            "description": description
        }

        return payload
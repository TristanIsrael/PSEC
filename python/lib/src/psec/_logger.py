from . import MqttClient, SingletonMeta
import logging

class Logger(metaclass=SingletonMeta):

    def setup(self, component_name:str, client_log:MqttClient):
        self.component_name = component_name
        self.client_log = client_log

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
        datetime = now.strftime(f"%Y-%m-%d %H:%M:%S.{now.microsecond // 1000:03d}")

        payload = {
            "component": self.component_name,
            "module": module,
            "datetime": datetime,
            "description": description
        }

        return payload
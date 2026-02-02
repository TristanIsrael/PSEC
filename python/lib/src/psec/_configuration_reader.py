import json
import os
from . import SingletonMeta

class Configuration():

    def __init__(self, name:str, identifier:dict, settings:dict):
        self.name = name
        self.identifier = identifier
        self.settings = settings

class ConfigurationReaderPrivate(metaclass=SingletonMeta):

    __configurations = {}

    # Cached value for the current system configuration
    system_configuration = None

    def __init__(self):
        self.__load_default_configuration()
        self.__load_configurations()

    def __load_configurations(self):
        with open(file="/etc/psec/topology.json", mode='r', encoding="utf-8") as file:
            data = json.load(file)

            confs = data.get("configurations", {})
            for conf in confs:
                name = conf.get("name", "unknown")
                identifier = conf.get("identifier", {})
                settings = conf.get("settings", {})

                if name != "unknown":
                    print(f"Loaded configuration {name}")
                    self.__configurations[name] = Configuration(name, identifier, settings)

    def __load_default_configuration(self):
        with open(file="/etc/psec/topology.json", mode='r', encoding="utf-8") as file:
            data = json.load(file)

            print("Loading default configuration")
            settings = {}
            for key, value in data.items():
                # We load all settings except "configurations"
                if key != "configurations":
                    settings[key] = value

            self.__configurations["default"] = Configuration("default", "default", settings)

    def get_configurations(self):
        return self.__configurations
    
class ConfigurationReader():

    @staticmethod
    def get_configuration(name:str) -> dict:
        """ Returns a configuration by its name. """
        reader = ConfigurationReaderPrivate()

        configs = reader.get_configurations()

        if name not in configs.keys():
            print(f"Configuration {name} not found")
            
        return configs.get(name, {})
        

    @staticmethod
    def __merge_settings(reference:dict, new_values:dict) -> dict:
        for key, value in new_values.items():
            if key in reference and isinstance(reference[key], dict) and isinstance(value, dict):
                ConfigurationReader.__merge_settings(reference[key], value)
            else:
                reference[key] = value
              

    @staticmethod
    def get_configuration_for_system() -> dict:
        """ Returns the configuration for the running system.

        The configuration returned will be composed of the keys from topology.json:
        - the global configuration (all keys except "configuration")
        - the specific configuration which matches the identifier defined in the configuration section

        The global settings are loaded and then overwritten by specific configuration settings if any.        
        """

        if ConfigurationReaderPrivate().system_configuration is not None:
            # If we have it in cache we return the cached value
            return ConfigurationReaderPrivate().system_configuration

        configs = ConfigurationReaderPrivate().get_configurations()

        # First we load the default configuration
        settings = configs.get("default", {}).settings

        for name, config in configs.items():
            if name == "default":
                continue

            # For each configuration we compare the fields of the identifier dict
            identifier = config.identifier

            values_verified = False
            for key, value in identifier.items():
                filename = f"/sys/class/dmi/id/{key}"

                if not os.path.exists(filename):
                    print(f"The sysfs file {filename} does not exist")
                    # So we ignore this key

                system_value = ConfigurationReader.__read_dmi_file(filename)

                # We have a key:value, and a DMI value, we compare both
                if system_value != value:
                    values_verified = False
                    break
                else:
                    values_verified = True

            # If all values have been verified, we have a configuration
            if values_verified:
                # Now we merge the values
                ConfigurationReader.__merge_settings(settings, config.settings)
            
        # We update the cache
        ConfigurationReaderPrivate().system_configuration = settings

        return settings
  
    @staticmethod
    def __read_dmi_file(filename:str) -> str:
        with open(file=filename, mode='r',encoding="utf-8") as data:
            return data.readline().strip()
        
        return ""
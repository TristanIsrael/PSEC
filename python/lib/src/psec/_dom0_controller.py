import threading
import subprocess
import time
import psutil
from . import Constantes, __version__
from . import Logger, FichierHelper, Parametres, Cles
from . import ResponseFactory
from . import MqttClient, Topics, MqttHelper, NotificationFactory
from . import System, EtatComposant
from . import LibvirtHelper

class Dom0Controller():
    """ @brief The Dom0 controller listens to messages coming from other controllers or Domains and provides responses.    

    """    

    __mqtt_lock = threading.Event()
    __is_shutting_down = False

    def __init__(self, mqtt_client: MqttClient):
        self.mqtt_client = mqtt_client

        # Handle Mqtt messages
        self.mqtt_client.on_connected = self.__on_mqtt_connected
        self.mqtt_client.on_message = self.__on_mqtt_message
        
        Logger().setup("System controller", mqtt_client)


    def start(self):
        """ @brief Starts the controller by connecting to the messaging.
        """
        self.mqtt_client.start()
        self.__mqtt_lock.wait()
    

    def __on_mqtt_connected(self):
        Logger().debug("Starting Dom0 controller")
        self.mqtt_client.subscribe(f"{Topics.LIST_FILES}/request")
        self.mqtt_client.subscribe(f"{Topics.FILE_FOOTPRINT}/request")
        self.mqtt_client.subscribe(f"{Topics.SHUTDOWN}/request")
        self.mqtt_client.subscribe(f"{Topics.RESTART_DOMAIN}/request")
        self.mqtt_client.subscribe(Topics.GUI_READY)
        self.mqtt_client.subscribe(f"{Topics.SYSTEM_INFO}/request")
        self.mqtt_client.subscribe(f"{Topics.ENERGY_STATE}/request")
        self.mqtt_client.subscribe(f"{Topics.DELETE_FILE}/request")
        self.mqtt_client.subscribe(Topics.DISCOVER_COMPONENTS)
        self.mqtt_client.subscribe(f"{Topics.PING}/request")


    def __on_mqtt_message(self, topic:str, payload:dict):
        # The message will be handled in a thread        
        threading.Thread(target=self.__message_worker, args=(topic, payload, )).start()


    def __message_worker(self, topic:str, payload:dict):
        """ Cette fonction traite uniquement les messages destinés au Dom0 """
        
        try:
            if topic == f"{Topics.LIST_FILES}/request":
                self.__handle_list_files(payload)
            elif topic == f"{Topics.FILE_FOOTPRINT}/request":
                self.__handle_file_footprint(payload)
            elif topic == f"{Topics.SHUTDOWN}/request":
                self.__handle_shutdown(payload)
            elif topic == f"{Topics.RESTART_DOMAIN}/request":
                self.__handle_restart_domain(payload)
            elif topic == Topics.GUI_READY:
                self.__handle_gui_ready(payload)
            elif topic == f"{Topics.ENERGY_STATE}/request":
                self.__handle_energy_state()
            elif topic == f"{Topics.SYSTEM_INFO}/request":
                self.__handle_system_info()
            elif topic == f"{Topics.DELETE_FILE}/request":
                self.__handle_delete_file(payload)
            elif topic == f"{Topics.DISCOVER_COMPONENTS}/request":
                self.__handle_discover_components()
            elif topic == f"{Topics.PING}/request":
                self.__handle_ping(payload)
        except Exception:
            Logger.print("An exception occured while handling the message")



    def __handle_list_files(self, payload:dict) -> None:
        if not self.__is_storage_request(payload):
            return 

        # Récupère la liste des fichiers                    
        fichiers = FichierHelper.get_files_list(Constantes.REPOSITORY, True)

        # Génère la réponse
        response = ResponseFactory.create_response_list_files(Constantes.REPOSITORY, fichiers)
        self.mqtt_client.publish(f"{Topics.LIST_FILES}/response", response)


    def __handle_file_footprint(self, payload:dict) -> None:
        if not self.__is_storage_request(payload):
            return
                    
        filepath = payload.get("filepath")
        disk = payload.get("disk")

        if filepath is None or disk is None:
            # S'il manque un argument on envoie une erreur
            Logger().error("La commande est incomplète : il manque le nom du disque et/ou le chemin du fichier")
            return
        
        # Calcule l'empreinte
        repository_path = Parametres().parametre(Cles.CHEMIN_DEPOT_DOM0)
        footprint = FichierHelper.calculate_footprint(f"{repository_path}/{filepath}")

        Logger().info(f"Footprint = {footprint}")
        
        # Génère la réponse
        response = ResponseFactory.create_response_file_footprint(filepath, disk, footprint)
        self.mqtt_client.publish(f"{Topics.FILE_FOOTPRINT}/response", response)


    def __handle_shutdown(self, payload:dict):
        if self.__is_shutting_down:
            return
        
        Logger().warn("System shutdown requested!")
        self.__is_shutting_down = True

        # There is currently no rule for the shutdown, so we accept it
        response = ResponseFactory.create_response_shutdown(True)
        self.mqtt_client.publish(f"{Topics.SHUTDOWN}/response", response)

        # We wait 5 seconds to let the GUIs and clients acknowledge the information
        time.sleep(5)

        # Then we shut the system down
        cmd = ["poweroff"]
        subprocess.run(cmd)


    def __handle_restart_domain(self, payload:dict):
        if not MqttHelper.check_payload(payload, ["domain_name"]):
            Logger().error(f"Missing argument domain_name in the topic {Topics.RESTART_DOMAIN}")
            return
        
        domain_name = payload.get("domain_name", "")
        self.__reboot_domain(domain_name)


    def __handle_gui_ready(self, payload:dict):
        # When GUI is ready we hide the splash screen
        cmd = ["killall", "feh"]
        subprocess.run(cmd)


    def __is_storage_request(self, payload:dict) -> bool:
        if payload.get("disk") is not None:
            return payload.get("disk") == Constantes.REPOSITORY
        else:
            return False


    def __reboot_domain(self, domain_name:str):
        if LibvirtHelper.reboot_domain(domain_name):
            Logger().info(f"Rebooting domain {domain_name}")
            response = ResponseFactory.create_response_restart_domain(domain_name, True)
            self.mqtt_client.publish(f"{Topics.RESTART_DOMAIN}/response", response)
        else:
            Logger().error(f"The domain {domain_name} won't reboot")
            response = ResponseFactory.create_response_restart_domain(domain_name, False)
            self.mqtt_client.publish(f"{Topics.RESTART_DOMAIN}/response", response)

        #cmd = ["xl", "reboot", domain_name]
        #res = subprocess.run(cmd)

        #if res.returncode == 0:
        #    Logger().info(f"Rebooting domain {domain_name}")
        #    response = ResponseFactory.create_response_restart_domain(domain_name, True)
        #    self.mqtt_client.publish(f"{Topics.RESTART_DOMAIN}/response", response)
        #else:
        #    Logger().error(f"The domain {domain_name} won't reboot")
        #    response = ResponseFactory.create_response_restart_domain(domain_name, False)
        #    self.mqtt_client.publish(f"{Topics.RESTART_DOMAIN}/response", response)


    def __handle_energy_state(self):
        battery = psutil.sensors_battery()

        if battery:
            payload = NotificationFactory.create_notification_energy_state(battery)
            self.mqtt_client.publish(f"{Topics.ENERGY_STATE}/response", payload)


    def __handle_system_info(self):
        payload = System.get_system_information()
 
        self.mqtt_client.publish(f"{Topics.SYSTEM_INFO}/response", payload)

    def __handle_delete_file(self, payload:dict):
        if not MqttHelper.check_payload(payload, ["disk", "filepath"]):
            Logger().error(f"The command {Topics.DELETE_FILE} misses argument(s)", "Dom0")
            return

        disk = payload["disk"]

        if disk != Constantes.REPOSITORY:
            # This file is not stored in the repository so we ignore it
            return

        filepath = payload["filepath"]
        repository_path = Parametres().parametre(Cles.CHEMIN_DEPOT_DOM0)
        storage_filepath = f"{repository_path}/{filepath}"

        if not FichierHelper().remove_file(storage_filepath):
            Logger().error(f"Removal of file {filepath} from repository failed")
        else:
            Logger().info(f"Removed file {filepath} from repository")
        
    def __handle_discover_components(self):
        payload = ResponseFactory.create_response_component_state(
            Constantes.PSEC_SYSTEM_CONTROLLER,
            "System main controller",
            "Dom0",
            EtatComposant.READY
        )

        self.mqtt_client.publish(f"{Topics.DISCOVER_COMPONENTS}/response", payload)

    def __handle_ping(self, payload):
        ping_id = payload.get("id", "")
        data = payload.get("data", "")
        sent_at = payload.get("sent_at", "")
        payload = ResponseFactory.create_response_ping(ping_id, "Dom0", data, sent_at)

        self.mqtt_client.publish(f"{Topics.PING}/response", payload)

    
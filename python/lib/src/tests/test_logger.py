import unittest
import time
import os
import threading
import logging
import subprocess
import psutil
import io
from datetime import datetime
from contextlib import redirect_stdout
from safecor import Logger, MqttFactory, Topics, System, RequestFactory

def is_mosquitto_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == "mosquitto":
            return True
    return False

class TestLogger(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Verify Mosquitto
        if not is_mosquitto_running():
            cls.mosquitto_proc = subprocess.Popen(["mosquitto"])
            time.sleep(1)

            if not is_mosquitto_running():
                raise RuntimeError("Mosquitto could not be started")
        else:
            cls.mosquitto_proc = None

        # Start Safecor MQTT client
        cls.setup_lock = threading.Event()
        cls.messages = []
        cls.mqtt_client = MqttFactory.create_mqtt_network_dev("test_logger")
        cls.mqtt_client.add_connected_callback(cls.on_mqtt_connected)
        cls.mqtt_client.add_message_callback(cls.on_message)
        cls.mqtt_client.start()
        if not cls.setup_lock.wait(1.0):
            raise RuntimeError("Could not connect to Safecor API")

    @classmethod
    def tearDownClass(cls):
        if cls.mosquitto_proc:
            cls.mosquitto_proc.terminate()
            cls.mosquitto_proc.wait()

        if os.path.exists("/tmp/safecor.log"):
            os.remove("/tmp/safecor.log")

    @classmethod
    def on_mqtt_connected(cls):
        print("Connected to Safecor API")
        Logger().setup("test_logger", cls.mqtt_client, logging.INFO, True, "/tmp/safecor.log")
        cls.setup_lock.set()

    @classmethod
    def on_message(cls, topic:str, payload:dict):
        cls.messages.append( { "topic": topic, "payload": payload} )

    def test_logfile(self):
        if os.path.exists("/tmp/safecor.log"):
            os.remove("/tmp/safecor.log")
                
        Logger().error("TEST")
        Logger().error("TEST2")
        time.sleep(0.5)
        self.assertTrue(os.path.exists("/tmp/safecor.log"))

        with open("/tmp/safecor.log", "r") as logfile:
            log = logfile.read()
            self.assertTrue(len(log.split("\n")), 3)
            self.assertTrue(log.endswith("[error] test_logger - TEST2\n"))

    def test_write_logfile(self):
        cls = self.__class__
        cls.mqtt_client.subscribe(f"{Topics.CREATE_FILE}/request")
        cls.mqtt_client.publish(Topics.SAVE_LOG, { "disk": "out", "filename": "file.txt" })
        time.sleep(1.0)

        save_log = [d for d in cls.messages if d["topic"] == "system/events/save_log" and d["payload"] == {'disk': 'out', 'filename': 'file.txt'}]
        self.assertNotEqual( save_log, [] )

        create_file = [d for d in cls.messages if d["topic"] == "system/disks/create_file/request" and d["payload"] != {} ]
        self.assertNotEqual( create_file, [] )
        entry = create_file[0]
        self.assertEqual(entry["payload"]["filepath"], "/file.txt")
        self.assertEqual(entry["payload"]["disk"], "out")
        self.assertEqual(entry["payload"]["compressed"], True)

    def test_double_setup(self):
        cls = self.__class__

        self.assertTrue(Logger().is_setup())
        Logger().setup("another", cls.mqtt_client, logging.ERROR, False, "/tmp/another.log")

        self.assertEqual(Logger().module_name(), "test_logger")
        self.assertEqual(Logger().domain_name(), System.domain_name())
        self.assertEqual(Logger().log_level(), logging.INFO)
        self.assertTrue(Logger().is_recording())
        self.assertEqual(Logger().filename(), "/tmp/safecor.log")

    def test_format_logline(self):
        log = Logger().format_logline("This is a test")
        
        timestamp_str, message = log.split(" - ", 1)
        dt = datetime.fromisoformat(timestamp_str)

        date = dt.date()
        dtime = dt.time()

        dtnow = datetime.now()
        self.assertEqual(date, dtnow.date())
        self.assertEqual(dtnow.hour, dtime.hour)
        self.assertEqual(dtnow.minute, dtime.minute)
        self.assertEqual(message, "This is a test")

    def test_levels(self):
        if os.path.exists("/tmp/safecor.log"):
            os.truncate("/tmp/safecor.log", 0)
            
        Logger().set_log_level(logging.DEBUG)
        Logger().debug("Test debug")
        Logger().warn("Test warn")
        Logger().warning("Test warning")
        Logger().info("Test info")
        Logger().error("Test error")
        Logger().critical("Test critical")

        time.sleep(0.5)
        
        n_line = 1

        with open("/tmp/safecor.log", "r") as f:
            data = f.readlines()

            for line in data:
                if n_line == 1:
                    self.assertIn("[debug]", line)
                if n_line == 2:
                    self.assertIn("[warning]", line)
                if n_line == 3:
                    self.assertIn("[warning]", line)
                if n_line == 4:
                    self.assertIn("[info]", line)
                if n_line == 5:
                    self.assertIn("[error]", line)
                if n_line == 6:
                    self.assertIn("[critical]", line)

                n_line = n_line + 1
        
        self.assertEqual(n_line, 7)

        # Set a higher log level
        os.truncate("/tmp/safecor.log", 0)
        Logger().set_log_level(logging.WARN)
        Logger().debug("Test debug")
        Logger().warn("Test warn")
        Logger().warning("Test warning")
        Logger().info("Test info")
        Logger().error("Test error")
        Logger().critical("Test critical")

        time.sleep(0.5)
        
        n_line = 1

        with open("/tmp/safecor.log", "r") as f:
            data = f.readlines()

            for line in data:
                if n_line == 1:
                    self.assertIn("[warning]", line)
                if n_line == 2:
                    self.assertIn("[warning]", line)                
                if n_line == 3:
                    self.assertIn("[error]", line)
                if n_line == 4:
                    self.assertIn("[critical]", line)

                n_line = n_line + 1
        
        self.assertEqual(n_line, 5)
            
    def test_print(self):
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            Logger().print("This is a test")
            Logger().print("This is another test")

        log = buffer.getvalue()

        n_line = 1
        for line in log.split("\n"):
            if line == "":
                continue
            
            self.assertStartsWith(line, f"{datetime.now():%Y-%m-%d}")
            
            if n_line == 1:
                self.assertEndsWith(line, "This is a test")
            else:
                self.assertEndsWith(line, "This is another test")

            n_line = n_line + 1

    def test_set_loglevel_by_api(self):
        cls = self.__class__

        Logger().set_log_level(logging.INFO)
        msg = RequestFactory.create_request_set_log_level(logging.ERROR)
        cls.mqtt_client.publish(Topics.SET_LOG_LEVEL, msg)
        time.sleep(0.5)
        self.assertEqual(Logger().log_level(), logging.ERROR)


if __name__ == "__main__":
    unittest.main()
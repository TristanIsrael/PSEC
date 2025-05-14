from psec import Logger, MqttFactory, Topics
import unittest, time, os, threading, logging

class TestLogger(unittest.TestCase):       
    setup_lock = threading.Event()

    messages = list()

    def __on_mqtt_connected(self):
        Logger().setup("test_logger", self.mqtt_client, logging.INFO, True, "/tmp/psec.log")
        self.setup_lock.set()

    def test_logfile(self):
        os.remove("/tmp/psec.log")

        self.mqtt_client = MqttFactory.create_mqtt_network_dev("test_logger")
        self.mqtt_client.add_connected_callback(self.__on_mqtt_connected)
        self.mqtt_client.start()
        self.setup_lock.wait()
        Logger().info("TEST")
        Logger().info("TEST2")
        time.sleep(0.2)
        self.assertTrue(os.path.exists("/tmp/psec.log"))

        with open("/tmp/psec.log", "r") as logfile:
            log = logfile.read()
            self.assertTrue(len(log.split("\n")), 3)
            self.assertTrue(log.endswith("[info] test_logger - TEST2\n"))

    def __on_message(self, topic:str, payload:dict):
        self.messages.append( { "topic": topic, "payload": payload} )

    def test_write_logfile(self):
        self.mqtt_client = MqttFactory.create_mqtt_network_dev("test_logger")
        self.mqtt_client.add_connected_callback(self.__on_mqtt_connected)
        self.mqtt_client.add_message_callback(self.__on_message)
        self.mqtt_client.start()
        self.setup_lock.wait()        
        self.mqtt_client.subscribe("{}/request".format(Topics.CREATE_FILE))
        self.mqtt_client.publish(Topics.SAVE_LOG, { "disk": "out", "filename": "file.txt" })
        time.sleep(1.0)
        self.assertEqual(len(self.messages), 3)
        msg = self.messages[2]
        self.assertEqual(msg.get("topic"), "system/disks/create_file/request")
        payload = msg.get("payload")
        self.assertEqual(payload.get("filepath"), "/file.txt")
        self.assertEqual(payload.get("disk"), "out")
        self.assertNotEqual(payload.get("contents"), "")
        self.assertTrue(payload.get("compressed"))

if __name__ == "__main__":    
    unittest.main()
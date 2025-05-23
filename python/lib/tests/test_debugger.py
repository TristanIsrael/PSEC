from psec import MqttFactory, Api, Debugging, System
import threading

class TestDebugger():
    NB_ITERATIONS = 100
    DATA_LENGTH = 32
    iterations = 0
    event = threading.Event()

    def callback(self, result:dict):
        print(result)

        self.iterations += 1
        if self.iterations == self.NB_ITERATIONS:
            self.event.set()

        print(f"{self.NB_ITERATIONS - self.iterations} iterations left")

    def on_connected(self):
        debugging = Debugging()
        debugging.benchmark_messaging(System.domain_name(), self.callback, self.NB_ITERATIONS, self.DATA_LENGTH)

    def start(self):
        self.iterations = 0

        client=MqttFactory.create_mqtt_network_dev("test")
        #client=MqttFactory.create_mqtt_client_domu("test")
        Api().add_ready_callback(self.on_connected)
        Api().start(client)        
        self.event.wait()

if __name__ == "__main__":
    TestDebugger().start()

import subprocess, os, time, threading, select, socket
from psec import Constantes, Cles

broker_msg_socket = Constantes().constante(Cles.MQTT_MSG_BROKER_SOCKET)
broker_log_socket = Constantes().constante(Cles.MQTT_LOG_BROKER_SOCKET)

BUFFER_SIZE = 4096

class UnixSocketTunneler:
    def __init__(self, socket1_path, socket2_path):
        self.socket1_path = socket1_path
        self.socket2_path = socket2_path
        self.stop_event = threading.Event()

    def handle_connection(self, src_socket:socket.socket, dst_socket:socket.socket):
        """
        Continuously forward data from src_socket to dst_socket.
        """
        while not self.stop_event.is_set():
            try:
                data = src_socket.recv(BUFFER_SIZE)
                if not data:  # Connection closed
                    break                
                dst_socket.sendall(data)
            except (socket.error, BrokenPipeError):
                break

    def tunnel(self):
        """
        Set up connections and manage bidirectional tunneling.
        """
        while not self.stop_event.is_set():
            try:
                # Create sockets
                sock1 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock2 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

                # Connect to the specified sockets
                sock1.connect(self.socket1_path)
                sock2.connect(self.socket2_path)

                print(f"Connected: {self.socket1_path} --> {self.socket2_path}")

                # Start threads for bidirectional tunneling
                thread1 = threading.Thread(target=self.handle_connection, args=(sock1, sock2))
                thread2 = threading.Thread(target=self.handle_connection, args=(sock2, sock1))

                thread1.start()
                thread2.start()

                # Wait for both threads to finish
                thread1.join()
                thread2.join()

            except socket.error as e:
                print(f"Socket error: {e}. Retrying in 5 seconds...")
                time.sleep(5)  # Wait before retrying
            finally:
                sock1.close()
                sock2.close()

    def stop(self):
        """
        Stop the tunneling process.
        """
        self.stop_event.set()

def create_log_tunnel(socket:str):
    tunneler = UnixSocketTunneler(socket, broker_log_socket)
    threading.Thread(target=tunneler.tunnel).start()
    #threading.Thread(target=main, args=(socket, broker_log_socket,)).start()

def create_msg_tunnel(socket:str):
    tunneler = UnixSocketTunneler(socket, broker_msg_socket)
    threading.Thread(target=tunneler.tunnel).start()
    #threading.Thread(target=main, args=(socket, broker_msg_socket,)).start()

def wait_for_broker_socket() -> bool:
    print("Waiting for MQTT Broker sockets...")
    
    while True:
        if os.path.exists(broker_log_socket) and os.path.exists(broker_msg_socket):
            return True
        else:
            time.sleep(1)

def watch_log_sockets():
    print("Looking for log mqtt sockets")

    cmd = "find /var/run/ -name '*-log.sock'"
    sockets = set()

    while True:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        files = result.stdout.strip().split("\n")
        
        new_files = set(files) - sockets
        for file in new_files:
            if file == "":
                continue
            print(f"New logging socket found : {file}")
            create_log_tunnel(file)            

        sockets.update(files)
        time.sleep(1)
    

def watch_msg_sockets():
    print("Looking for msg mqtt sockets")

    cmd = "find /var/run/ -name '*-msg.sock'"
    sockets = set()

    while True:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        files = result.stdout.strip().split("\n")
        
        new_files = set(files) - sockets
        for file in new_files:
            if file == "":
                continue
            print(f"New messaging socket found : {file}")
            create_msg_tunnel(file)            

        sockets.update(files)
        time.sleep(1)

if __name__ == "__main__":
    wait_for_broker_socket()

    threading.Thread(target=watch_log_sockets).start()
    threading.Thread(target=watch_msg_sockets).start()

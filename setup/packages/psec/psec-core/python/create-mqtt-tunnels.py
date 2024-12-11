import subprocess, os, time, threading, select, socket
from psec import Constantes, Cles

broker_msg_socket = Constantes().constante(Cles.MQTT_MSG_BROKER_SOCKET)

BUFFER_SIZE = 4096
DEBUG = True

def hexdump(data, prefix=""):
    """Print binary data in hexdump format."""
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        hex_bytes = " ".join(f"{byte:02x}" for byte in chunk)
        ascii_bytes = "".join(chr(byte) if 32 <= byte <= 126 else '.' for byte in chunk)
        print(f"{prefix}{i:04x}: {hex_bytes:<48} {ascii_bytes}")

class UnixSocketTunneler:
    #__connection_lost = threading.Event()

    def __init__(self, client_socket_path, broker_socket_path, n_socket:int):
        self.client_socket_path = client_socket_path
        self.broker_socket_path = broker_socket_path
        self.n_socket = n_socket
        self.stop_event = threading.Event()


    def handle_connection(self, client_socket:socket.socket, broker_socket:socket.socket, direction:str):
        """
        Continuously forward data from src_socket to dst_socket.
        """
        client_socket.setblocking(False)
        broker_socket.setblocking(False)

        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)

                if DEBUG:
                    hexdump(data, prefix=f"{direction}> ")

                if not data:  # Connection closed
                    print("Error: data empty")
                    break
                broker_socket.sendall(data)
            except BlockingIOError:
                continue
            except (socket.error, BrokenPipeError) as e:                
                print("handle_connection", e)
                break
            finally:
                client_socket.close()
                broker_socket.close()

        print(f"Loop {direction} terminated")

    '''
    def purge_pv_channel(self, socket:socket.socket, nb_bytes:int=4096):        
        #sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        #sock.connect(sock_path)        

        print("Clear the buffer for the socket {}".format(self.client_socket_path))        
        bytes = 0
        socket.setblocking(False) 

        try:
            while bytes < nb_bytes:
                try:
                    data = socket.recv(4096)
                    if not data:
                        break  
                except BlockingIOError:
                    break  # Buffer is empty
        finally:
            socket.setblocking(True)
            print("The buffer of {} is empty".format(self.client_socket_path))        
    '''

    def create_client_socket_and_wait_for_connection(self) -> socket.socket:
        client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_sock.connect(self.client_socket_path)

        print(f"Connected to {self.client_socket_path} and waiting for data")

        ready_to_read, _, _ = select.select([client_sock], [], [])
        if client_sock in ready_to_read:
            print("Client has connected.")
            return client_sock

    def tunnel(self):
        """
        Set up connections and manage bidirectional tunneling.
        We need to connect to the broken only when there is an incoming connection from a client
        """
        while not self.stop_event.is_set():
            try:
                # Create broker socket                
                broker_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

                # Connect to the client and wait for data
                client_sock = self.create_client_socket_and_wait_for_connection()

                broker_socket_path = "/var/run/mosquitto/mqtt_msg_{}.sock".format(self.n_socket)
                print("Connect to the broker on socket {}".format(broker_socket_path))                                
                broker_sock.connect(broker_socket_path)                

                # Start threads for bidirectional tunneling
                thread1 = threading.Thread(target=self.handle_connection, args=(client_sock, broker_sock, "A->B"))
                thread2 = threading.Thread(target=self.handle_connection, args=(broker_sock, client_sock, "B->A"))

                thread1.start()
                thread2.start()

                thread1.join()
                thread2.join()

                print(f"Tunnel {self.client_socket_path} <--> {self.broker_socket_path} is broken")
            except socket.error as e:
                print(f"{self.client_socket_path} --> {self.broker_socket_path}. Socket error: {e}.")
                #time.sleep(5)  # Wait before retrying
            finally:
                #print("Close connections")
                client_sock.close()
                broker_sock.close()
                time.sleep(1)  # Wait before retrying

    def stop(self):
        """
        Stop the tunneling process.
        """
        self.stop_event.set()

def create_msg_tunnel(client_socket:str, n_socket:int):
    tunneler = UnixSocketTunneler(client_socket, broker_msg_socket, n_socket)
    #threading.Thread(target=tunneler.tunnel).start()
    tunneler.tunnel()

def wait_for_broker_socket() -> bool:
    print("Waiting for MQTT Broker sockets...")
    
    cmd = "find /var/run/ -name '{}'".format(broker_msg_socket)

    while True:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        files = result.stdout.strip().split("\n")
        
        if len(files) == 0:
            time.sleep(1)
        else:
            print("Broker sockets ready")
            return True

def watch_msg_sockets():
    print("Looking for msg mqtt sockets")

    cmd = "find /var/run/ -name '*-msg.sock'"
    sockets = set()
    n_socket = 1

    while True:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        files = result.stdout.strip().split("\n")
        
        new_files = set(files) - sockets
        for file in new_files:
            if file == "":
                continue
            print(f"New messaging socket found : {file}")
            threading.Thread(target=create_msg_tunnel, args=(file, n_socket)).start()
            n_socket += 1

        sockets.update(files)
        time.sleep(1)

if __name__ == "__main__":
    wait_for_broker_socket()

    threading.Thread(target=watch_msg_sockets).start()

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
    __connection_lost = threading.Event()

    def __init__(self, client_socket_path, broker_socket_path):
        self.client_socket_path = client_socket_path
        self.broker_socket_path = broker_socket_path
        self.stop_event = threading.Event()


    def handle_connection(self, client_socket:socket.socket, broker_socket:socket.socket, direction:str):
        """
        Continuously forward data from src_socket to dst_socket.
        """
        client_socket.setblocking(False)
        broker_socket.setblocking(False)

        while not self.__connection_lost.is_set():
            try:
                data = client_socket.recv(BUFFER_SIZE)

                # Verify if this is a disconnection frame
                # if data == b'e000'

                if DEBUG:
                    hexdump(data, prefix=f"{direction}> ")
                if not data:  # Connection closed
                    print("Error: data empty")
                    break                
                broker_socket.sendall(data)
            except BlockingIOError:
                if self.__connection_lost.is_set():
                    break
            except (socket.error, BrokenPipeError) as e:                
                print("handle_connection", e)                
                break        

        self.__connection_lost.set()
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

    def tunnel(self):
        """
        Set up connections and manage bidirectional tunneling.
        """
        while not self.stop_event.is_set():
            try:
                # Create sockets
                self.client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.broker_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

                # Connect to the specified sockets
                self.client_sock.connect(self.client_socket_path)
                self.broker_sock.connect(self.broker_socket_path)

                print(f"Connected: {self.client_socket_path} --> {self.broker_socket_path}")

                # Purge the socket's buffer for the client
                #self.purge_pv_channel(client_sock, 32)
                # If the client has not disconnected properly we need to send
                # the disconnection string to the MQTT broker

                # Start threads for bidirectional tunneling
                thread1 = threading.Thread(target=self.handle_connection, args=(self.client_sock, self.broker_sock, "A->B"))
                thread2 = threading.Thread(target=self.handle_connection, args=(self.broker_sock, self.client_sock, "B->A"))

                thread1.start()
                thread2.start()

                # Wait for both threads to finish
                #self.__connection_lost.wait()                
                thread1.join()                
                thread2.join()

                print(f"Tunnel {self.client_socket_path} <--> {self.broker_socket_path} is broken")
            except socket.error as e:
                print(f"{self.client_socket_path} --> {self.broker_socket_path}. Socket error: {e}.")
                #time.sleep(5)  # Wait before retrying
            finally:
                print("Close connections")
                self.client_sock.close()
                self.broker_sock.close()
                self.__connection_lost.clear()
                time.sleep(1)  # Wait before retrying

    def stop(self):
        """
        Stop the tunneling process.
        """
        self.stop_event.set()

def create_msg_tunnel(client_socket:str):
    tunneler = UnixSocketTunneler(client_socket, broker_msg_socket)
    #threading.Thread(target=tunneler.tunnel).start()
    tunneler.tunnel()

def wait_for_broker_socket() -> bool:
    print("Waiting for MQTT Broker sockets...")
    
    while True:
        if os.path.exists(broker_msg_socket):
            return True
        else:
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
            threading.Thread(target=create_msg_tunnel, args=(file,)).start()

        sockets.update(files)
        time.sleep(1)

if __name__ == "__main__":
    wait_for_broker_socket()

    threading.Thread(target=watch_msg_sockets).start()

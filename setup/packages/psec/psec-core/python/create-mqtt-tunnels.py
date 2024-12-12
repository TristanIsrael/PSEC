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

    '''
    def handle_connection(self, socket_left:socket.socket, socket_right:socket.socket, direction:str):
        """
        Continuously forward data from src_socket to dst_socket.
        """
        #client_socket.setblocking(False)
        #broker_socket.setblocking(False)

        while True:
            try:
                data = socket_left.recv(BUFFER_SIZE)

                if DEBUG:
                    hexdump(data, prefix=f"{direction}> ")

                if not data:  # Connection closed
                    print("Error: data empty")
                    break
                socket_right.sendall(data)            
            except (socket.error, OSError) as e:                
                print("Connection error:", e)
            finally:
                print("Close sockets")
                socket_left.close()
                socket_right.close()            

        print(f"Loop {direction} terminated")
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
        while True:
            try:
                # Create broker socket                
                broker_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

                # Connect to the client and wait for data
                client_sock = self.create_client_socket_and_wait_for_connection()

                broker_socket_path = "/var/run/mosquitto/mqtt_msg_{}.sock".format(self.n_socket)                                       
                broker_sock.connect(broker_socket_path)                
                print("Connected to the broker on socket {}".format(broker_socket_path))         

                '''
                # Start threads for bidirectional tunneling
                thread1 = threading.Thread(target=self.handle_connection, args=(client_sock, broker_sock, "A->B"))
                thread2 = threading.Thread(target=self.handle_connection, args=(broker_sock, client_sock, "B->A"))

                thread1.start()
                thread2.start()

                thread1.join()
                thread2.join()
                '''

                sockets = [client_sock, broker_sock]

                while True:
                    # Utiliser select pour attendre les sockets prêtes en lecture
                    readable, writable, _ = select.select(sockets, sockets, [])

                    # Lecture sur socket_left et écriture sur socket_right
                    if client_sock in readable:
                        try:
                            data = client_sock.recv(4096)
                            if data:
                                if DEBUG:
                                    hexdump(data, prefix=f"client>broker ")
                                if broker_sock in writable:
                                    broker_sock.sendall(data)
                                else:
                                    print("socket_right n'est pas prête à écrire.")
                            else:
                                print("socket_left s'est fermée.")
                                break  # Sortir de la boucle si la socket est fermée
                        except OSError as e:
                            print(f"Erreur lors de la lecture sur socket_left : {e}")
                            break

                    # Lecture sur socket_right et écriture sur socket_left
                    if broker_sock in readable:
                        try:
                            data = broker_sock.recv(4096)
                            if data:
                                if DEBUG:
                                    hexdump(data, prefix=f"broker>client ")
                                if client_sock in writable:
                                    client_sock.sendall(data)
                                else:
                                    print("socket_left n'est pas prête à écrire.")
                            else:
                                print("socket_right s'est fermée.")
                                break  # Sortir de la boucle si la socket est fermée
                        except OSError as e:
                            print(f"Erreur lors de la lecture sur socket_right : {e}")
                            break

                # Fermeture des sockets proprement
                client_sock.close()
                broker_sock.close()

                print(f"Tunnel {self.client_socket_path} <--> {self.broker_socket_path} is broken")
            except socket.error as e:
                print(f"{self.client_socket_path} --> {self.broker_socket_path}. Socket error: {e}.")
                #time.sleep(5)  # Wait before retrying
            finally:
                #print("Close connections")
                client_sock.close()
                broker_sock.close()
                time.sleep(1)  # Wait before retrying


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

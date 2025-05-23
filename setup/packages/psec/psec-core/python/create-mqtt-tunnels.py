import subprocess, os, time, threading, select, socket
from psec import Constantes, Cles, Logger

broker_msg_socket = Constantes().constante(Cles.MQTT_MSG_BROKER_SOCKETS)

BUFFER_SIZE = 4096
DEBUG = False
DEBUG_HEX = False

def hexdump(data, prefix=""):
    """Print binary data in hexdump format."""
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        hex_bytes = " ".join(f"{byte:02x}" for byte in chunk)
        ascii_bytes = "".join(chr(byte) if 32 <= byte <= 126 else '.' for byte in chunk)
        Logger.print(f"{prefix} {i:04x}: {hex_bytes:<48} {ascii_bytes}")

    Logger.print("EOF")

class UnixSocketTunneler:

    def __init__(self, client_socket_path, broker_socket_path, n_socket:int):
        self.client_socket_path = client_socket_path
        self.broker_socket_path = broker_socket_path
        self.n_socket = n_socket

    def tunnel(self, messaging_socket_path:str):
        """
        Set up connections and manage bidirectional tunneling.
        We need to connect to the broken only when there is an incoming connection from a client
        """
        client_to_broker_buffer = b''
        broker_to_client_buffer = b''

        while True:
            # The tunnel is re-created as much as necessary to stay alive

            try:
                # Create broker socket
                broker_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

                # Connect to the client and wait for data
                client_sock = self.__create_client_socket_and_wait_for_connection()

                broker_socket_path = f"/tmp/mqtt_msg_{self.n_socket}.sock"
                broker_sock.connect(broker_socket_path)
                Logger.print(f"Connected to the broker on socket {broker_socket_path} and tunneling with {messaging_socket_path}")
                
                while True:
                    rlist = []
                    wlist = []

                    # Watch broker and client socket for incoming data
                    rlist.append(client_sock)
                    rlist.append(broker_sock)

                    # Write only when there are data to be sent
                    if client_to_broker_buffer:
                        wlist.append(broker_sock)
                    if broker_to_client_buffer:
                        wlist.append(client_sock)

                    readable, writable, _ = select.select(rlist, wlist, [])

                    # If the client sent data
                    if client_sock in readable:
                        try:
                            data = client_sock.recv(100)
                            if data:
                                client_to_broker_buffer += data
                                self.__debug_data(data, messaging_socket_path, "proxy")
                            else:
                                Logger.print(f"Client socket closed on {messaging_socket_path}.")
                                break
                        except BlockingIOError:
                            pass

                    # If the broker sent data
                    if broker_sock in readable:
                        try:
                            data = broker_sock.recv(100)
                            if data:
                                broker_to_client_buffer += data
                                self.__debug_data(data, broker_socket_path, "proxy")
                            else:
                                Logger.print(f"Broker socket closed on {broker_socket_path}.")
                                break
                        except BlockingIOError:
                            pass

                    # Send to the broker
                    if broker_sock in writable and client_to_broker_buffer:
                        try:
                            sent = broker_sock.send(client_to_broker_buffer)
                            self.__debug_data(client_to_broker_buffer, "proxy", broker_socket_path)
                            client_to_broker_buffer = client_to_broker_buffer[sent:]
                        except BlockingIOError:
                            pass

                    # Send to the client
                    if client_sock in writable and broker_to_client_buffer:
                        try:
                            sent = client_sock.send(broker_to_client_buffer)
                            if DEBUG:
                                self.__debug_data(client_to_broker_buffer, "proxy", messaging_socket_path)
                            broker_to_client_buffer = broker_to_client_buffer[sent:]
                        except BlockingIOError:
                            pass
                    
            except socket.error as e:
                Logger.print(f"{self.client_socket_path} --> {self.broker_socket_path}. Socket error: {e}.")
            finally:
                client_sock.close()
                broker_sock.close()
                time.sleep(1)  # Wait before retrying

    def __create_client_socket_and_wait_for_connection(self) -> socket.socket:
        client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_sock.connect(self.client_socket_path)

        Logger.print(f"Connected to {self.client_socket_path} and waiting for data")

        ready_to_read, _, _ = select.select([client_sock], [], [])
        if client_sock in ready_to_read:
            Logger.print("Client has sent its first byte.")
            return client_sock
        
    def __debug_data(self, data, emitter, receiver):
        if DEBUG_HEX:
            hexdump(data, f"from {emitter} to {receiver}")
        else:
            Logger.print(f"from {emitter} to {receiver}: {data}")


def create_msg_tunnel(client_socket:str, n_socket:int):
    Logger.print(f"Creating new tunnel with client socket {client_socket} with ID {n_socket}.")
    tunneler = UnixSocketTunneler(client_socket, broker_msg_socket, n_socket)
    tunneler.tunnel(client_socket)


def wait_for_broker_socket() -> bool:
    Logger.print("Waiting for MQTT Broker sockets...")
    
    cmd = "find /var/run/ -name '{}'".format(broker_msg_socket)

    while True:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        files = result.stdout.strip().split("\n")
        
        if len(files) == 0:
            time.sleep(1)
        else:
            Logger.print("Broker sockets ready")
            return True


def watch_msg_sockets():
    Logger.print("Looking for msg mqtt sockets")

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
            Logger.print(f"New messaging socket found : {file}")
            threading.Thread(target=create_msg_tunnel, args=(file, n_socket)).start()
            n_socket += 1

        sockets.update(files)
        time.sleep(1)


if __name__ == "__main__":
    wait_for_broker_socket()

    threading.Thread(target=watch_msg_sockets).start()

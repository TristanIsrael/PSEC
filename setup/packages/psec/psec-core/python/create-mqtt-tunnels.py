import subprocess, os, time, threading, select, socket
from psec import Constantes, Cles

broker_msg_socket = Constantes().constante(Cles.MQTT_MSG_BROKER_SOCKET)
broker_log_socket = Constantes().constante(Cles.MQTT_LOG_BROKER_SOCKET)

def tunnel_data(src_socket, dst_socket):
    """
    Tunnel data between two Unix sockets without buffering or delay.
    Continuously transfers data in both directions until the connection is closed.
    """
    while True:
        # Using select to check for data in both sockets without blocking
        rlist, _, _ = select.select([src_socket, dst_socket], [], [], 1)

        for sock in rlist:
            data = sock.recv(4096)
            if data:
                # Send the received data to the other socket
                if sock is src_socket:
                    dst_socket.sendall(data)
                else:
                    src_socket.sendall(data)
            else:
                # If no data, the socket is closed
                return

def reconnect_socket(socket_path):
    """
    Attempts to reconnect the socket to the specified Unix socket path.
    """
    while True:
        try:
            # Try to create a new socket connection
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(socket_path)
            print(f"Connected to {socket_path}")
            return sock
        except socket.error as e:
            # If the connection fails, wait and try again
            print(f"Failed to connect to {socket_path}, retrying in 5 seconds... Error: {e}")
            time.sleep(5)

def main(src_socket_path, dst_socket_path):
    """
    Main function that connects to two Unix sockets and tunnels data between them.
    """
    while True:
        # Attempt to reconnect both source and destination sockets
        print(f"Connecting to source socket: {src_socket_path}")
        src_socket = reconnect_socket(src_socket_path)

        print(f"Connecting to destination socket: {dst_socket_path}")
        dst_socket = reconnect_socket(dst_socket_path)

        try:
            # Tunnel data between the two sockets
            tunnel_data(src_socket, dst_socket)
        except Exception as e:
            # If an error occurs, print it and attempt to reconnect
            print(f"An error occurred: {e}. Reconnecting...")
        finally:
            # Ensure sockets are closed if the connection fails
            src_socket.close()
            dst_socket.close()

def create_log_tunnel(socket:str):
    threading.Thread(target=main, args=(socket, broker_log_socket,)).start()

def create_msg_tunnel(socket:str):
    threading.Thread(target=main, args=(socket, broker_msg_socket,)).start()

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

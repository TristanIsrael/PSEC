import subprocess, os, time, threading, atexit
from psec import Constantes, Cles

broker_msg_socket = Constantes.constante(Cles.MQTT_MSG_BROKER_SOCKET)
broker_log_socket = Constantes.constante(Cles.MQTT_LOG_BROKER_SOCKET)

def create_log_tunnel(socket:str):
    cmd = ["socat", "UNIX-CONNECT:{}".format(socket), "UNIX-CONNECT:{}".format(broker_log_socket)]
    subprocess.Popen(cmd)

def create_msg_tunnel(socket:str):
    cmd = ["socat", "UNIX-CONNECT:{}".format(socket), "UNIX-CONNECT:{}".format(broker_msg_socket)]
    subprocess.Popen(cmd)

def wait_for_broker_socket() -> bool:
    print("Waiting for MQTT Broker sockets...")
    
    while True:
        if os.path.exists(broker_log_socket) and os.path.exists(broker_msg_socket):
            return True
        else:
            time.sleep(1)

def watch_log_sockets():
    print("Looking for log mqtt sockets")

    cmd = "find /var/run -name '*-log.sock'"
    sockets = set()

    while True:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        files = result.stdout.strip().split("\n")
        
        new_files = set(files) - sockets
        for file in new_files:
            print(f"New logging socket found : {file}")
            create_log_tunnel(file)

        sockets.update(files)
        time.sleep(1)
    

def watch_msg_sockets():
    print("Looking for msg mqtt sockets")

    cmd = "find /var/run -name '*-msg.sock'"
    sockets = set()

    while True:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        files = result.stdout.strip().split("\n")
        
        new_files = set(files) - sockets
        for file in new_files:
            print(f"New messaging socket found : {file}")
            create_msg_tunnel(file)

        sockets.update(files)
        time.sleep(1)

if __name__ == "__main__":
    wait_for_broker_socket()

    threading.Thread(target=watch_log_sockets).start()
    threading.Thread(target=watch_msg_sockets).start()

import socket, os, threading, sys, pty, termios
from . import Journal

class MockXenbus():
    __dom0_socket_path = ""    
    __dom0_socket = None    
    __domain_name = "Unknown"
    __dom0_current_connection = None
    __domu_serial_port_master = None # This script side
    __domu_serial_port_master_path = ""
    #__domu_serial_port_slave = None  # The peer side
    __domu_serial_port_slave_path = ""

    __journal = Journal("MockXenbus")
        
    def __init__(self):
        pass

    def start(self, domain_name:str, dom0_socket:str) -> bool:
        self.__dom0_socket_path = dom0_socket

        self.__domain_name = domain_name
        self.__journal.debug("Creating Mock Xenbus for {}".format(domain_name))

        # Verify that files don't exist
        if os.path.exists(self.__dom0_socket_path):
            self.__journal.debug("INFO - The file {} already exists. Trying to remove it.".format(self.__dom0_socket_path))
            os.remove(self.__dom0_socket_path)

        if os.path.exists(self.__dom0_socket_path):
            self.__journal.debug("ERROR - The file {} still exists...".format(self.__dom0_socket_path))
            return False

        if not self.__create_dom0_socket():
            self.__journal.debug("ERROR - Could not create the Dom0 socket")
            return False

        if not self.__open_domu_serial_port():
            self.__journal.debug("ERROR - Could not open DomU serial port")
            return False
        
        self.__journal.debug("Mock Xenbus for {} is ready at:".format(domain_name))
        self.__journal.debug("  - socket {}".format(self.__dom0_socket_path))
        self.__journal.debug("  - serial port slave {}".format(self.__domu_serial_port_slave_path))

        threading.Thread(target=self.__monitor_domu_serial_port).start()
        threading.Thread(target=self.__monitor_dom0_socket).start()

        return True

    def dom0_socket_path(self):
        return self.__dom0_socket_path
    
    def domu_serial_port_path(self):
        return self.__domu_serial_port_slave_path

    ###
    # Private functions
    #
    def __create_dom0_socket(self):
        self.__journal.debug("... creating a socket for Dom0")

        try:
            self.__dom0_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.__dom0_socket.bind(self.__dom0_socket_path)
            self.__dom0_socket.listen(1)
        except Exception as e:
            print(e)
            return False

        return True 
    
    def __monitor_dom0_socket(self):    
        self.__journal.debug("... now waiting for connections on Dom0 socket...")

        while True:
            conn, _ = self.__dom0_socket.accept()
            self.__journal.debug("Connection received on Dom0 socket for {}".format(self.__domain_name))
            self.__dom0_current_connection = conn

            try:
                while True:
                    data = conn.recv(128)
                    
                    if not data:
                        continue

                    self.__journal.debug("Received {} bytes on Dom0 socket for {}".format(len(data), self.__domain_name))
                    self.__journal.debug(data)
                    os.write(self.__domu_serial_port_master, data)
                    self.__journal.debug("Data writen on master serial port: {}".format(data))
                    #self.__domu_serial_port_master.write(data)
            except Exception as e:
                self.__journal.debug("Error with the socket")
                self.__journal.debug(e)
            #finally:
            #    conn.close()
            #    self.__dom0_socket.close()
            #    os.remove(self.__dom0_socket_path)
            #    self.__journal.debug("Socket removed")
    
    def __open_domu_serial_port(self):
        self.__journal.debug("... creating a serial port on DomU for {}".format(self.__domain_name))

        try:
            master_fd, slave_fd = pty.openpty()
            if master_fd != None and slave_fd != None:
                self.__domu_serial_port_master = master_fd
                self.__domu_serial_port_slave_path = os.ttyname(slave_fd)
                os.close(slave_fd)
                return True
            else:
                self.__journal.debug("ERROR - Something went wrong...")
                return False
        except Exception as e:
            print(e)
            return False         
    
    def __monitor_domu_serial_port(self):
        self.__journal.debug("Start monitoring the DomU serial port for {}".format(self.__domain_name))

        while True:
            data = os.read(self.__domu_serial_port_master, 128)
            if len(data) == 0:
                continue

            self.__journal.debug("Received {} bytes on serial port for {}".format(len(data), self.__domain_name))
            self.__journal.debug(data)
            if self.__dom0_current_connection is not None:
                self.__dom0_current_connection.send(data)

if __name__ == "__main__":
    print("Xenbus MOCK tool")

    if len(sys.argv) < 2:
        print("Arguments missing: DOM0_SOCKET_PATH")
        exit(99)

    mock = MockXenbus()
    mock.start(sys.argv[1])

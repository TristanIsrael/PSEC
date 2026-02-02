import os
import socket
import logging
from psec import Logger

SOCKET_PATH = "/var/run/psec_logger.sock"

SEVERITY = {
    0: logging.CRITICAL,
    1: logging.CRITICAL,
    2: logging.CRITICAL,
    3: logging.ERROR,
    4: logging.WARNING,
    5: logging.WARNING,
    6: logging.INFO,
    7: logging.DEBUG
}

try:
    os.unlink(SOCKET_PATH)
except FileNotFoundError:
    pass

with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as s:
    s.bind(SOCKET_PATH)

    while True:
        data = s.recv(1024)
        if data and b'-' in data:
            parts = data.split(b' - ', 1)
            severity = parts[0].decode().strip()
            msg = parts[1].decode().strip()

            psec_severity = SEVERITY.get(severity, logging.WARNING)

            if psec_severity == logging.DEBUG:
                Logger().debug(msg)
            elif psec_severity == logging.INFO:
                Logger().info(msg)
            elif psec_severity == logging.WARNING:
                Logger().warning(msg)
            elif psec_severity == logging.ERROR:
                Logger().error(msg)
            elif psec_severity == logging.CRITICAL:
                Logger().critical(msg)
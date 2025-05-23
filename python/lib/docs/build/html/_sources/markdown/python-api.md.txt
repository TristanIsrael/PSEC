# Python API

This document describes how the Python API works.

*Work in progress*

## File Locations

Some files have a fixed location or are configurable via parameters:

| File | Description | Parameter | Default Value | Notes |
|---|---|---|---|---|
| Log file | Domain-local log file | CHEMIN_JOURNAL_LOCAL | /var/log/panoptiscan.log | The file is only created if the parameter `ACTIVE_JOURNAL_LOCAL` is set to True |
| Python library | Contains all Python classes required for the system | None | System's `python` directory | The library is packaged in the file `panoptiscan_lib[...]-none-any.whl` and is installed automatically during system deployment |
| DomU messaging socket | Messaging sockets for communication with each DomU are stored in a common directory | CHEMIN_SOCKETS_MSG | /var/run/panoptiscan/*-msg.sock | |
| DomU logging socket | Logging sockets for each DomU are stored in a common directory | CHEMIN_SOCKETS_LOG | /var/run/panoptiscan/*-log.sock | |
| Global configuration | Defines the behavior of Python components | CHEMIN_FICHIER_CONFIG_GLOBAL | /etc/panoptiscan/global.conf | |

## Packaging

...
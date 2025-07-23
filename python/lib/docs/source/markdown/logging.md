# Logging

This document describes the logging strategy and the mechanisms implemented.

## Features

Logging occurs at two levels:
- Operating system: services can record a number of events in files located in `/var/log` or send them to a log manager such as `syslog`.
- Business application: applications and the platform generate events related to the operation of the product.

Only business events are covered in this documentation.

## Architecture

Logging uses the system messaging infrastructure through specific topics `system/events`.

## Debug Level

The debug level is set using the command `system/events/set_loglevel`.

## Emitting an Event

Sharing log information is done via notifications `system/events/[loglevel]` where `loglevel` can be:
- `debug`: Debugging information
- `info`: General information
- `warn`: Warning
- `error`: Software error impacting only part of the system functions
- `critical`: Software or hardware error preventing the system from operating

Event emission is simplified through the Python class `Logger`. It is used as follows:

`Logger().debug("Debug message", "Module name")`  
or `Logger().info("Informational message")`.

## Recording

The platform automatically saves all events at or above the level defined by the `set_loglevel` command (or `info` by default) into a file that can be copied or downloaded on demand. The logging level can be configured to keep only a subset of events.

## Retrieving the Log

The command to retrieve the log is `system/events/save_log`.

## Syslog

The package `psec-syslog` can be installed in a Domain in order to provide `syslog` facility.

When this package is installed, all `syslog` logs with the tag `PSEC` are redirected to the PSEC logger. This gives you an opportunity to use standard logging services and libraries for logging, including for services you install in the Domains.

Additionally, the commande `logger` can be used in the shell to send log to PSEC, for example:
```
$ logger -t PSEC My message log
```
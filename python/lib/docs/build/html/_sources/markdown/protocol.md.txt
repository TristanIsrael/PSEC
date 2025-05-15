# Protocol
 
This documents explains the MQTT topics and their respective payloads.
 
The chapter are presented by function.
 
## Disks and file management
 
This chapter presents the functions related to disks and files.
 
### List connected disks
 
*Requests the list of external storage disks connected to this system.*
 
Request topic: `system/disks/list_disks/request`
Request payload : `{}`
 
Response topic: `system/disks/list_disks/response`
Response payload :
```
{
    "disks": [ "disk1", "disk2", ... ]
}
```
 
Response fields:
- `disks` (list): The list of disk names as strings.
 
### List files of a disk
 
*Requests the list of files contained in a disk.*
 
Request topic: `system/disks/list_files/request`
Request payload :
```
{
    "disk": "disk1",
    "recursive": false,
    "from_dir": ""
}
```
 
Request fields:
- `disk` (str): The name of the disk this request relates to.
- `recursive` (bool): if *true*, the listing will be done on every subdirectory in the tree, starting from *from_dir*. **Default is *false*.**.
- `from_dir`(str): if set, the files list will contain only the files of this directory, and subdirectories if *recursive* is set. **Default is ""**.
 
Response topic: `system/disks/list_files/response`
Response payload :
```
{
    "disk": "disk1"
    "files": [
        {
            "type": "file",
            "path": "/",
            "name": "my_file.txt",
            "size": "1234"
        },        
        ...
    ]
}
```
 
Response fields:
- `disk` (str): The disk the file belongs to.
- `files` (list): The list of files.
  - `type` (str): "file" or "folder".
  - `path` (str): The complete file path.
  - `name` (str): The file (or folder) name.
  - `size` (int): The size in bytes. *For a folder, this field is absent.*
 
### Copy a file in the repository
 
*Copy a file from an external storage to the local repository of the system*.
 
Request topic: `system/disks/read_file/request`
 
Request payload:
```
{
    "disk": "disk1",
    "filepath": "/my/folder/my_file.txt"
}
```
 
Request fields:
- `disk` (str) : The disk the file belongs to.
- `filepath` (str) : The complete path of the file.
 
Response topic: *See New file notification*
 
### Delete a file
 
*Delete a file from a disk, including the repository*
 
Request topic: `system/disks/delete_file/request`
 
Request payload:
```
{
    "disk": "disk1",
    "filepath": "/my/folder/my_file.txt"
}
```
 
Request fields:
- `disk` (str) : The disk the file belongs to.
- `filepath` (str) : The complete path of the file.
 
### Calculate a file fingerprint
 
*Calculates the unique fingerprint of a file. The current algorihm is MD5.*
 
Request topic: `system/disks/file_footprint/request`
 
Request payload:
```
{
    "disk": "disk1",
    "filepath": "/my/folder/my_file.txt"
}
```
 
Request fields:
- `disk` (str) : The disk the file belongs to.
- `filepath` (str) : The complete path of the file.
 
Response topic: `system/disks/file_footprint/response`
 
Response payload:
```
{
    "disk": "disk1",
    "filepath": "/my/folder/my_file.txt,    
    "footprint": "12cfd565ff54caa12"
}  
```
 
Response fields:
- `disk` (str) : The disk the file belongs to.
- `filepath` (str) : The complete path of the file.
- `footprint` (str) : The footprint of the file as an MD5 hash.
 
### Create a new file
 
*Create a new file on a disk, including the repository*.
 
Request topic: `system/disks/create_file/request`
Request payload:
```
{
    "disk": "disk1",
    "filepath": "/my/folder/my_file.txt,
    "data": "KJsh76S8912Hgsgfd54222Rtfg=="
    "compressed": true
}
```
Request fields:
- `disk` (str) : The disk the file belongs to.
- `filepath` (str) : The complete path of the file.
- `data` (str) : The data to be written in the file.
- `compressed` (bool) : In case of binary data, they can be compressed using the *GNU zip* algorithm and this field must be *true*. If data are not compressed, this field must be *false*. **Default is false**.
 
Response payload: *See New file notification*.
 
## Workflow
 
This chapter presents the functions related to the state of the system.
 
### Shutdown the system
 
*Ask the system to shut down*.
 
Request topic: `system/workflow/shutdown/request`
Request payload: `{}`
 
Response topic: `system/workflow/shutdown/response`
Response payload:
```
{
    "state": "accepted",
    "reason: ""
}
```
Response fields:
- `state` (str): *accepted* if the system accepted the shutdown or *refused* if the system rejected the shutdown.
- `reason` (str): If the system refused to shut down, this field contains the reason.
 
### Restart a Domain
 
*Ask the restart of a Domain*.
 
Request topic: `system/workflow/restart/request`
Request payload:
```
{
    "domain_name": "my_domain
}
```
Request fields:
- `domain_name` (str): The name of the Domain to restart. It must match an existing Domain like `sys-usb`, `sys-gui`, or a Domain defined in the `topology.json` file.
 
Response topic: `system/workflow/restart/response`
Response payload:
```
{
    "state": "accepted",
    "reason: ""
}
```
Response fields:
- `domain_name` (str): The domain name which was queried to restart.
- `state` (str): *accepted* if the system accepted the shutdown or *refused* if the system rejected the shutdown.
- `reason` (str): If the system refused to shut down, this field contains the reason.
 
## Logging
 
This chapter presents logging functions.
 
### Add a debug log
 
Topic: `system/events/debug`
Payload:
```
    "component": "my component",
    "module": "my module",
    "datetime": "2025-04-02 03:04:05",
    "description": "The problem..."
```
Fields:
- `component` (str): The system component's name.
- `module` (str): The work module name.
- `datetime` (str): The date and time when the event occured.
- `description` (str): A literal description of the event.
 
### Add an information log
 
Topic: `system/events/info`
 
*See Add a debug log*.
 
### Add a warning log
 
Topic: `system/events/warning`
 
*See Add a debug log*.
 
### Add an error log
 
Topic: `system/events/error`
 
*See Add a debug log*.
 
### Add a critical log
 
Topic: `system/events/critical`
 
*See Add a debug log*.
 
### Set the log level
 
*Define the log level under which the events will be ignored*.
 
Topic: `system/events/set_loglevel`
Payload:
```
{
    "level": "info"
}
```
Fields:
- `level` (str): The level of log under which events are not recorded (see python logging).
 
### Save the log into a file
 
*Save all logs into a file*.
 
Topic : `system/events/save_log`
Payload:
```
{
    "disk": "disk1",
    "filename": "logfile.txt"
}
```
Fields:
- `disk` (str): The disk on which the log file must be created.
-  `filename` (str): The complete file path of the log file.
 
## Miscellaneous
 
This chapter presents miscellaneous functions of the system.
 
### Discover the components of the system
 
Topic : `system/disks/list_disks`
 
### Get the energy state
 
Topic : `system/disks/list_disks`
 
### Get information on the system
 
Topic : `system/disks/list_disks`
 
## Notifications
 
This chapter presents the notifications sent by different components.
 
### A new file is available
 
*This notification is sent when a file has been copied or created on a disk, including the repository*.
 
Topic: `system/disks/new_file`
Payload:
```
{
    "disk": "disk1",
    "filepath", "/a/folder/my_file.txt",
    "source_footprint": "acd653c5a8b988cbdbabd65",
    "dest_footprint": "acd653c5a8b988cbdbabd65"
}
```
Fields:
- `disk` (str): The disk on which the file hase been created.
- `filepath` (str): The complete path of the file.
- `source_footprint` (str): The fingerprint of the original source file.
- `dest_footprint` (str): The fingerprint of the file after the copy. *It must match the source_footprint value*.
 
### The state of disk changed
 
*A disk has been connected or disconnected from the system.
 
Topic : `system/disks/state`
Payload:
```
{
    "disk": "disk1",
    "state": "connected"
}
```
Fields:
- `disk` (str): The name of the disk which state has changed.
- `state`  (str): *connected* if the disk has been connected, otherwise *disconnected*.
 
### The GUI is ready
 
*When the GUI is ready, the splash screen must be removed.*
 
Topic: `system/workflow/gui_ready`
 
Payload: `{}`
 
## Notes
 
This chapter gives additional information.
 
### Repository
 
The repository can be referenced as `__repository__`.
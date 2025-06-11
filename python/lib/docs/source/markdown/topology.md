# Topology

This document describes the format of the topology file.

This is a typical `topology.json`:
```
{
    "usb": {
        "use": 1
    },
    "gui": {
        "use": 1,
        "app-package": "app-gui",
        "memory": 1000,
        "app-package": "app-apk-package",
        "screen": {
            "rotation": 0
        }
    },    
    "vcpu": {
        "groups": {
            "sys-gui": 0.2,
            "my_group": 0.8
        }
    },
    "business": {
        "domains": [
            {
                "name": "myapp-function1",
                "package": "myapp-function1",
                "memory": 4096,
                "vcpu_group": "my_group"
            },
            {
                "name": "myapp-function2",
                "package": "myapp-function2",
                "memory": 4096,
                "vcpu_group": "my_group"
            }
        ]
    }

}
```

## Keywords details

Here is the detail of the keys:
| Key | Type | Description |
|--|--|--|
| usb.use | int | Set to 1 if the Domain `sys-usb` should be setup and used, else 0.|
| gui.use | int | Set to 1 if the Domain `sys-gui` should be setup and used, else 0. `sys-usb` should be used when the product comes with a GUI. |
| gui.memory | int | Defines the memory, in MB, which should be allocated to `sys-gui` to run the GUI application. |
| gui.app-package | string | When `sys-gui` starts, it must install a package (APK) which provides the GUI application and its dependencies. |
| gui.screen.rotation | int | Defines the rotation of the screen if needed, for example on a tablet. Accepted valued are: 0, 90, 180 or 270. |
| *business.domains* | *array* | *This sections defines the domains which will be created on startup.* |
| business.domains.<entry>.name | string | Gives a name to the Domain. |
| business.domains.<entry>.package | string | Defines the package (APK) which will be installed in the Domain. |
| business.domains.<entry>.memory | int | Defines the memory, in MB, which whould be allocated to the Domain. |

## Resource management

This sections explains how resources can be distributed into the system.

Resources (CPU, memory) can be affected to Domains (sys-gui and business Domains) as portions of the platform resources.

### vCPU management

The following rules apply:

- the Dom0 and sys-usb Domains can't be configured. 
  - Dom0 will have the 2 first vCPUs unless the system has less than 4, so he gets only the first.
  - sys-usb will have the same vCPUs as Dom0
- the configurable groups are:
  - sys-gui will have the 2 next vCPUs by default unless the system has less than 4, so he gets only the second one. This value can be modified in topology.json.
  - the rest can be divided in groups and affected to the Domains.

The proportions are:
- 15% to Dom0/sys-usb (shared) -> minimum value is 1
- 75% for the rest of the system:
  - 20% to sys-gui by default (overridable)
  - 80% to the business Domains divisible into groups.

Groups of vCPUs are declared in the section `vcpu.groups` which represents 100% of the allocatable vCPUs (75% of the system).

Then each business domain can have a group allocated using the keyword `vcpu_group`.

Example :

```
"vcpu": {
    "groups": {
        "my_group": 0.8
    }
} 

"business": {
    "domains": [
        {
            "name": "myapp-function1",            
            "vcpu_group": "my_group"
        }
    ]
}

```
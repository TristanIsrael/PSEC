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
    "business": {
        "domains": [
            {
                "name": "myapp-function1",
                "package": "myapp-function1",
                "memory": 4096,
                "cpu": 0.5
            },
            {
                "name": "myapp-function2",
                "package": "myapp-function2",
                "memory": 4096,
                "cpu": 0.5
            }
        ]
    }

}
```

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
| business.domains.<entry>.cpu | float | Defines the percentage of the whole CPU cores which should be allocated to the Domain. Accepted values are between 0.0 (0%) and 1.0 (100%). |
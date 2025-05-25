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
    
    "network": {
        "repositories": [
            "http://<mirror url>/depots/alpine/main",
            "http://<mirror url>/depots/alpine/community"
        ],
        "releases": "http://<mirror url>/isos/"
    }
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

More details to come.
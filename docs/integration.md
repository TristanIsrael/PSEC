# Integration

This document describes the integration process which leads to the creation of a product.

## Glossary

| Term | Meaning |
|--|--|
| Domain | A domain is a virtual machine hosted by Xen hypervisor |
| DomD or Domain Driver | A DomD is a specialized domain dedicated to managind a specific hardward resource (GPU, USB, etc) |

## Topology and security mechanisms

The first this to understand is the topology and the security mechanisms. Security mainly relies on **isolation** of the functions inside the system.
This, accessing (read and copy) of external drives connected on USB is handled by a specific virtual machine called a Driver Domain (DomD). In PSEC this DomD is named `sys-usb`.

Designing a product upon PSEC is mainly a matter of urbanization of the functions. When dealing with machine resources you will call PSEC core functions. When dealing with user interactions and other business functions you will build your own virtual machines.

### Defining the topology

The topology can be defined in a file located at `/etc/psec/topology.json`. The DomD are fixed, you can only modify some settings. In this file you will be able to set your own domains and the Alpine package which will be deployed inside.

We strongly *encourage* to urbanize the system with this rule in mind : *One function per domain*.

The file `topology.json` lets you to define the domains list and the relations between them, in the case you want to establish communication channels between your domains or to send/receive messages or inputs.

The default typical `topology.json` is:

```
{
    "usb": {
        "use": 1
    },
    "gui": {
        "use": 1,
        "app-package": "saphir-gui"
    },
    "business": {
        "repository": "https://repository.local/myrepo",
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

## Creating a product

Creating a product is mainly a matter of :
- creating a main Alpine package containing a `topology.json` file.
- creating different specific Alpine packages for the business functions.

### Data sources

The system needs to download dependencies (packages, configuration) on different sources.

The file `/etc/psec/constants.sh` defines the default sources :

| Constant | Default value | Description |
|--|--|--|
| ALPINE_VERSION | `3.20` | Defines the Alpine version to use with the product. The URL of the packages repository depends on this constant|
| PSEC_PUBLIC_REPOSITORY | `https://alefbet.net/wp-content/uploads/repositories/PSEC` | Defines the place where the PSEC packages are stored. Can be a local server. |
| ALPINE_PUBLIC_ROOT | `http://dl-cdn.alpinelinux.org/alpine` | Defines the URL of the official Alpine mirror used to download Alpine packages |

# Integration

This document describes the integration process which leads to the creation of a product.

## Glossary

| Term | Meaning |
|--|--|
| Dom0 | The Domain0 is the virtual machine in charge of the orchestration of other VMs and the communication capabilities |
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

See [topology documentation](topology.md) for details about the file format.

## Create a product

Creating a product is mainly a matter of :
- creating a main Alpine package defining the topology of the system.
- creating different specific Alpine packages for the business functions.

**Alpine packages**

The main package of the product is in charge of:
- defining the topology of the system by providing a `topology.json` file
- listing all the dependencies with other packages.

### Main package

**APKBUILD**

The `depends` parameter file **must** contain `psec-core`.

**Post install**

The post install script of the package must call the script `/usr/lib/psec/bin/post-install.sh`. This will create the virtual machines, create the local repository, start the core services and make the system ready, including the GUI.

### GUI package

The GUI must be provided into 2 packages :
- One package in charge of creating the Domain.
- One package in charge of deploying the GUI into the Domain.
  - The package **must** depend on `psec-gui-base`.

### Data sources

The system needs to download dependencies (packages, configuration) on different sources.

The file `/etc/psec/constants.sh` defines the default sources :

| Constant | Default value | Description |
|--|--|--|
| ALPINE_VERSION | `3.20` | Defines the Alpine version to use with the product. The URL of the packages repository depends on this constant|
| PSEC_PUBLIC_REPOSITORY | `https://alefbet.net/wp-content/uploads/repositories/PSEC` | Defines the place where the PSEC packages are stored. Can be a local server. |
| ALPINE_PUBLIC_ROOT | `http://dl-cdn.alpinelinux.org/alpine` | Defines the URL of the official Alpine mirror used to download Alpine packages |

You can override these parameters to match your needs. 

## Compatibiliy with the hardware

PSEC provides a versatile environment compatible with different hardware (PC, tablets). Perhaps you will need to deploy the system on a new hardware or a hardware with which PSEC is not yet compatible.

This section provides information on the integration process on a new hardware.

If you want to know how to create configuration-specific profiles, see this [chapter](#create-a-configuration-specific-profile)

### Enumerate the components

You need to gather the list of hardware components:
- CPU
- GPU
- PCI buses

This can be done by booting on any Linux Live CD and use both `lcpci` and `lshw` tools.

### Blacklist a PCI USB bus

Use cases :
- On some hardware, there are PCI USB buses which cannot be grabbed by XEN and therefore cannot be captured by the `sys-usb` DomD in PCI passthrough.
- For security reasons you want to avoid a PCI bus to be used by the system.

That PCI bus must be *blacklisted* in the `topology.json` file of the product this way:

```
{
    "pci": {
        "blacklist": "00:0d.0"
    }
}
```

This section blacklists the PCI bus `0000:00:0d.0` which won't be captured by sys-usb nor the Dom0.

## Create a configuration-specific profile

When you product targets very different hardware configurations you may need to differenciate the behaviour and adapt to the real configuration. For example, when using a tablet, the screen layout can be rotated by 90 degrees.

This sections helps you creating configuration-specific profiles.

A profile is a set of parameters applied to a specific configuration. The configuration is defined by some hardware characteristics.

Parameters which can be configured are:
- GRUB bootloader configuration
- Screen rotation
- PCI blacklist

Configurations are defined in the `topology.json` file in a specific section `configurations`.

Default topology layout (without specific configuration):
```
{    
    "usb": {
        "use": 1
    },
    "pci": {
        "blacklist": "00:0d.0"
    },
    "gui": {
        "use": 1,
        "memory": 2000,
        "app-package": "saphir-gui",        
        "screen": {
            "rotation": 90
        }
    },
    ...
```

Topology layout using specific configurations:
```
{
    "gui": {
        "use": 1,
        "app-package": "saphir-gui"        
    },
    "configurations": [
        {
            "name": "ZBook laptop",
            "identifier": "xxxxxx",
            "settings": {
                "usb": {
                    "use": 1
                },                
                "gui": {                    
                    "memory": 2000,                    
                    "screen": {
                        "rotation": 0
                    }
                },
            }
        },
        {
            "name": "Durabook R8",
            "identifier": "xxxxxx",
            "settings": {
                "usb": {
                    "use": 1
                },
                "pci": {
                    "blacklist": "00:0d.0"
                },
                "gui": {
                    "memory": 2500,
                    "screen": {
                        "rotation": 90
                    }
                }
            }
        }
    ]
}
```

The topology can mix global configuration and specific configuration settings. Specific settings will override global ones.

The configurations are differenciated with their DMI information:
```
# dmidecode -t 1
# dmidecode 3.6
Getting SMBIOS data from sysfs.
SMBIOS 2.7 present.

Handle 0x000C, DMI type 1, 27 bytes
System Information
	Manufacturer: HP
	Product Name: HP ZBook 15 G3
	Version:
	Serial Number: XXXXXXXXXX
	UUID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
	Wake-up Type: Power Switch
	SKU Number: 1JF54EP#ABF
	Family: 103C_5336AN
```

The configuration identifier can be composed of any field of the DMI structure as found in the *sysfs* directory `/sys/class/dmi/id/`. For example, if the configuration target a specific model of laptops, the SKU field can be used alone. If any laptop of the ZBook 15 G3 family are targetted, the field Product Name of Family can be used.

*Please notice that these information are encoded by each manufacturer, their representation can differ from a manufacturer to another*.

The encoding of the identifier can be done in a JSON structure as key:value:
```
{
    "gui": {
        "use": 1,
        "app-package": "saphir-gui"        
    },
    "configurations": [
        {
            "name": "ZBook laptop",
            "identifier": {
                "sys_vendor": "HP",
                "product_sku": "1JF54EP#ABF"
            },
            "settings": {
                ...
            }
        }
    ]
}
```
# Create or Update the Alpine Mirror

This documentation presents the implementation of the Alpine package repositories.

## Prerequisites

To perform this procedure, the following prerequisites must be met:

- Existing web server with unsecured access (no password or SSL certificate) for the *Alpine repositories*

## Principles

The repositories are designed to evolve over time and allow the Maintenance en Condition Opérationnelle (MCO) and the Maintenance en Condition de Sécurité (MCS) of the Alpine distribution installed on the thin clients, as well as the controller software (Panoptiscan) and the antivirus databases.

When a mirror is synchronized from the Internet, its numbering (for example 3.15.2) must be preserved and a symbolic link must be created to this directory to allow both systematic use of the latest repository version and use of a specific version when necessary (regression, testing, etc.)

## Procedure

- On the web server, create the root directory for the repositories; by convention, we will call this root [ALPINE] in the remainder of this document.

- Inside the [ALPINE] folder, create the subfolder `panoptiscan`.

- Inside the [ALPINE] folder, copy the official Alpine repository keeping the version name, for example 3.15.

- Create a symbolic link named `latest-stable` pointing to the official repository folder.

### Common Actions

Updates, even minor ones, almost always bring changes to the XEN and Linux kernels. These must be updated both on the repositories and on the deployment infrastructure.

**Before updating an existing repository, it is recommended to create a copy of it and keep it in order to be able to roll back in case of malfunction of the thin clients following the update. See below:**

- Create a new directory with the exact version number (3.15.5 and not 3.15): 
```
$ cd [ALPINE]
$ cp -r 3.15.4 3.15.5
```

- In a shell command line, navigate to the directory and start the update:
```
$ wget –mirror –no-parent https://dl-cdn.alpinelinux.org/alpine/v3.15/releases/x86_64/
```

>>> Create an automated update script

### Post-Update Actions

After updating the repositories, the deployment infrastructure must be upgraded. To do this, simply rerun the Ansible deployment playbook (see [Create the deployment infrastructure](support-infrastructure.md)).
# Development of PSEC

This document is intended to the developers of PSEC.

## Requirements

This section describes the requirements for building a development computer.

- PSEC uses `python 3` for the core services and scripts.
- An [Alpine build environment](https://wiki.alpinelinux.org/wiki/Setting_up_the_build_environment_on_HDD) must be prepared.

## Build the packages

The steps for building the packages are:
- `git clone` the project.
- Enter each source folder in the `setup` directory.
- Run `abuild checksum && abuild -r`.

The packages will be available in the folder `~/packages/psec/<arch>`.

## psec-alpine-iso

This package creates a modified ISO for the HVM DomU in a system running PSEC. It is a dependency for `psec-core`. 

It compiles the Linux kernel and adds modules needed in `sys-usb` and `sys-gui`, then it creates the ISO image used when booting the DomU.

*The compilation of the kernel is a very long process (multiple hours)*.

### Incremental build of the kernel

In the case you want to add a module or make tests with or without some modules you have to:
- Make a first complete build and keep all the data (`abuild -K`)
- Enter in the `src/psec-alpine-virt-x.xx/aports/main/linux-lts`
- Edit the file `virt.x86_64.config` file
- Enter in the directory `src/linux-x.xx`
- Execute `$ cp ../virt.x86-64.config .config`
- Execute `$ make olddefconfig`
- Execute `$ make prepare`
- Execute `$ make modules_prepare`
- Execute `$ make modules`

*The -j option should be used in make to accelerate the build.*

To compile only one module, execute `$ make drivers/the/module`. For exemple `$ make drivers/usb/serial/ftdi_sio.ko`.

*[Package the module]*

Then the ISO image should be built again with the command `$ ./mkimage.sh --profile virt --repository "$HOME"/packages/main --repository https://dl-cdn.alpinelinux.org/alpine/v$pkgver/main --arch x86_64 --outdir "$HOME"/iso`. 

Another way to test is to copy the modules directly from the build system to the testing system:
- Install the modules in a temporary folder : `$ make INSTALL_MOD_PATH=/tmp/modules modules_install`
- Module will be in `/tmp/lib/modules/6.x.x-virt` they can be copied to the target.
- On the target system, execute `# depmod -a` before using the new modules.
profile_diag() {
    profile_xen
    kernel_cmdline="$kernel_cmdline unionfs_size=512M console=ttyS0,115200 console=ttyUSB0,115200"
    syslinux_serial="0 115200"
    kernel_addons=""
    kernel_flavors="lts"
    xen_params=""
    apks="$apks xen xen-hypervisor safecor-diag"
    arch="x86_64"    
    apkovl="genapkovl-diag.sh"
}
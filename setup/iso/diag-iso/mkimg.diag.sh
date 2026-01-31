profile_diag() {
    profile_xen
    kernel_cmdline="unionfs_size=512M console=tty0 console=ttyS0,115200"
    syslinux_serial="0 115200"
    kernel_addons=""
    apks="$apks xen-hypervisor psec-diag"
    local _k _a
    for _k in $kernel_flavors; do
            apks="$apks linux-$_k"
            for _a in $kernel_addons; do
                    apks="$apks $_a-$_k"
            done
    done
    apkovl="genapkovl-diag.sh"
}
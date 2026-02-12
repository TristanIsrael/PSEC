build_safecor() {
	apk fetch --root "$APKROOT" --stdout xen-hypervisor | tar -C "$DESTDIR" -xz boot
}

section_safecor() {
	[ -n "${xen_params+set}" ] || return 0
	build_section xen $ARCH $(apk fetch --root "$APKROOT" --simulate xen-hypervisor | checksum)
}

profile_safecor() {
    profile_standard

    profile_abbrev="safecor"
    title="Safecor"
    desc="ISO image for Safecor apps"
    arch="x86_64"
		
    kernel_cmdline="$kernel_cmdline console=ttyS0,115200 console=ttyUSB0,115200"
    syslinux_serial="0 115200"
    kernel_addons=""
    kernel_flavors="lts"
    xen_params=""
    apks="$apks rng-tools xen xen-hypervisor syslinux"
    arch="x86_64"
}
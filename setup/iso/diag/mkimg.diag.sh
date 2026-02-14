profile_diag() {
    profile_safecor

    profile_abbrev="diag"
    title="Safecor Diag"
    desc="Diagnostic app for Safecor"
    kernel_cmdline="$kernel_cmdline autodetect_serial=no"
    apks="$apks safecor-diag"
    apkovl="genapkovl-diag.sh"
    hostname="safecor-diag"
    boot_addons=""   
}
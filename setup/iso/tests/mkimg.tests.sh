profile_diag() {
    profile_safecor

    profile_abbrev="tests"
    title="Safecor tests"
    desc="Functional tests app for Safecor"
    kernel_cmdline="$kernel_cmdline autodetect_serial=no"
    apks="$apks safecor-tests"
    apkovl="genapkovl-tests.sh"
    hostname="safecor-tests"
    boot_addons=""   
}
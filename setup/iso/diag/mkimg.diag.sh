section_splash() {
    local file="$1"
    local ext="${file##*.}"
    ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')

    if [ ! -f "$file" ]; then
        echo "The file '$file' does not exist"
        return 1
    fi

    if [ "$ext" != "ppm" ]; then
        # Convert to PPM
        local out="${file%.*}.ppm"
        echo "Convert splash to PPM format"
        magick convert "$file" "$out"
        file=$out
    fi

    msg Adding splash image $file to ISO at ${DESTDIR}
    cp $file ${DESTDIR}/fbsplash0.ppm

    return $?
}

profile_diag() {
    profile_safecor

    profile_abbrev="diag"
    title="Safecord Diag"
    desc="Diagnostic app for Safecor"
    kernel_cmdline="$kernel_cmdline autodetect_serial=no"
    apks="$apks safecor-diag"
    apkovl="genapkovl-diag.sh"
    hostname="safecor-diag"
    boot_addons=""
}
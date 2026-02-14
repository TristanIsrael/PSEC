build_splash() {    
    local file="$1"
    msg "Handling splash file $file"
    
    local ext="${file##*.}"
    ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')

    if [ ! -f "$file" ]; then
        msg "The splash file '$file' does not exist"
        return 1
    fi

    if [ "$ext" != "ppm" ]; then
        # Convert to PPM
        local out="${file%.*}.ppm"
        msg "Convert splash to PPM format"
        magick convert "$file" "$out"
        file=$out
    fi

    msg Adding splash image $file to ISO at ${DESTDIR}
    cp $file ${DESTDIR}/fbsplash0.ppm

    return $?
}

section_splash() {
    for splash_file in ./splash.ppm ./splash.png; do
        [ -f "$splash_file" ] && { msg "Splash file found: $splash_file"; break; }
    done

    if [ -e "$splash_file" ]; then 
        msg "No splash file provided in $PWD"
        return 0 # Not blocking
    fi

    build_section splash $splash_file
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
    splash_file="splash.ppm"
}
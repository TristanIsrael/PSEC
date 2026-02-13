add_splash() {
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

    cp $file ${DESTDIR}/fbsplash0.ppm

    return $?
}

setup_inittab_console() { 
    # Prevent any console to be added by initramfs-init
    return 0; 
}

profile_diag() {
    profile_safecor

    apks="$apks safecor-diag"
    apkovl="genapkovl-diag.sh"
    hostname="safecor-diag"
    boot_addons=""

    add_splash "splash.ppm"
}
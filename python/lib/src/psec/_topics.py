class Topics():
    # Groups
    SYSTEM = "system"
    DISKS = "{}/disks".format(SYSTEM)
    MISC = "{}/misc".format(SYSTEM)
    EVENTS = "{}/events".format(SYSTEM)
    DISCOVER = "{}/discover".format(SYSTEM)
    
    # Requests
    LIST_DISKS = "{}/list_disks".format(DISKS)
    LIST_FILES = "{}/list_files".format(DISKS)
    READ_FILE = "{}/read_file".format(DISKS)
    COPY_FILE = "{}/copy_file".format(DISKS)
    DELETE_FILE = "{}/delete_file".format(DISKS)
    BENCHMARK = "{}/benchmark".format(MISC)
    FILE_FOOTPRINT = "{}/file_footprint".format(DISKS)
    CREATE_FILE = "{}/create_file".format(DISKS)
    DISCOVER_COMPONENTS = "{}/components".format(DISCOVER)

    # Notifications
    NEW_FILE = "{}/new_file".format(DISKS)
    DISK_STATE = "{}/state".format(DISKS)

    # Miscelaneous
    KEEPALIVE = "mics/ping"

    # Logging
    ERROR = "{}/error".format(EVENTS)
    WARNING = "{}/warning".format(EVENTS)
    INFO = "{}/info".format(EVENTS)
    DEBUG = "{}/debug".format(EVENTS)

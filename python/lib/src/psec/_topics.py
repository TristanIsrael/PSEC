class Topics():
    # Groups
    SYSTEM = "system"
    DISKS = f"{SYSTEM}/disks"
    MISC = "{}/misc".format(SYSTEM)
    EVENTS = "{}/events".format(SYSTEM)
    DISCOVER = "{}/discover".format(SYSTEM)
    WORKFLOW = "{}/workflow".format(SYSTEM)
    ENERGY = "{}/energy".format(SYSTEM)
    
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
    SHUTDOWN = "{}/shutdown".format(WORKFLOW)
    RESTART_DOMAIN = "{}/restart_domain".format(WORKFLOW)

    # Notifications
    NEW_FILE = "{}/new_file".format(DISKS)
    DISK_STATE = "{}/state".format(DISKS)
    GUI_READY = f"{WORKFLOW}/gui_ready"

    # Miscelaneous
    KEEPALIVE = "{}/ping".format(MISC)
    ENERGY_STATE = "{}/state".format(ENERGY)
    SYSTEM_INFO = f"{SYSTEM}/info"

    # Logging
    ERROR = "{}/error".format(EVENTS)
    WARNING = "{}/warning".format(EVENTS)
    INFO = "{}/info".format(EVENTS)
    DEBUG = "{}/debug".format(EVENTS)
    SET_LOGLEVEL = "{}/set_loglevel".format(EVENTS)
    SAVE_LOG = "{}/save_log".format(EVENTS)
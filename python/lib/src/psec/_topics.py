class Topics():
    # Groups
    SYSTEM = "system"
    DISKS = f"{SYSTEM}/disks"
    MISC = f"{SYSTEM}/misc"
    EVENTS = f"{SYSTEM}/events"
    DISCOVER = f"{SYSTEM}/discover"
    WORKFLOW = f"{SYSTEM}/workflow"
    ENERGY = f"{SYSTEM}/energy"
    DEBUG = f"{SYSTEM}debug"

    # Disks and files management
    LIST_DISKS = f"{DISKS}/list_disks"
    LIST_FILES = f"{DISKS}/list_files"
    READ_FILE = f"{DISKS}/read_file"
    COPY_FILE = f"{DISKS}/copy_file"
    DELETE_FILE = f"{DISKS}/delete_file"
    FILE_FOOTPRINT = f"{DISKS}/file_footprint"
    CREATE_FILE = f"{DISKS}/create_file"
    NEW_FILE = f"{DISKS}/new_file"
    DISK_STATE = f"{DISKS}/state"

    # Workflow management
    SHUTDOWN = f"{WORKFLOW}/shutdown"
    RESTART_DOMAIN = f"{WORKFLOW}/restart_domain"
    GUI_READY = f"{WORKFLOW}/gui_ready"

    # Miscellaneous
    DISCOVER_COMPONENTS = f"{DISCOVER}/components"
    KEEPALIVE = f"{MISC}/ping"
    ENERGY_STATE = f"{ENERGY}/state"
    SYSTEM_INFO = f"{SYSTEM}/info"
    BENCHMARK = f"{MISC}/benchmark"

    # Logging
    ERROR = f"{EVENTS}/error"
    WARNING = f"{EVENTS}/warning"
    INFO = f"{EVENTS}/info"
    DEBUG = f"{EVENTS}/debug"
    SET_LOGLEVEL = f"{EVENTS}/set_loglevel"
    SAVE_LOG = f"{EVENTS}/save_log"

    # Debugging
    DEBUGGING = f"{SYSTEM}/debugging"
    PING = f"{DEBUGGING}/ping"
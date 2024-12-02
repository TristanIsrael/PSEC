class Topics():
    # Requests
    LIST_DISKS = "system/disks/list_disks"
    LIST_FILES = "system/disks/list_files"    
    READ_FILE = "system/disks/read_file"
    COPY_FILE = "system/disks/copy_file"
    DELETE_FILE = "system/disks/delete_file"
    BENCHMARK = "system/misc/benchmark"
    FILE_FOOTPRINT = "system/disks/file_footprint"
    CREATE_FILE = "system/disks/create_file"    
    DISCOVER_MODULES = "system/modules/discover"

    # Notifications
    NEW_FILE = "system/disks/new_file"
    DISK_STATE = "system/disks/state"

    # Miscelaneous
    KEEPALIVE = "mics/ping"

    # Logging
    ERROR = "system/events/error"
    WARNING = "system/events/warning"
    INFO = "system/events/info"
    DEBUG = "system/events/debug"

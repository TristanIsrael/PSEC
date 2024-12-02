import os, pyudev
from . import Logger, MqttClient, Topics, NotificationFactory

class DiskMonitor():
    """ Cette classe surveille un répertoire afin de détecter les ajout et suppression de fichiers et dossiers.

    Elle fonctionne en mode *polling* afin d'être compatible avec le protocole 9pfs de XEN qui ne prend pas en 
    charge les notifications de système de fichiers.

    La classe doit être instanciée avec le chemin du point de montage à surveiller (par exemple /mnt). 
    
    Connexion d'un support de stockage :
    Lorsqu'un support de stockage est connecté, un nouveau point de montage est créé par le système (cf udev/mdev) 
    dans le répertoire /mnt (par exemple /mnt/NO NAME). Dans ce cas, la notification SUPPORT_USB 
    sera émise.

    Déconnexion d'un support de stockage :
    Lorsqu'un support de stockage est retiré, le point de montage est effacé par le système (cf udev/mdev) dans 
    le répertoire /mnt. Dans ce cas, la notification SUPPORT_USB sera émise.
    """    

    disks = {}

    def __init__(self, folder:str, mqtt_client:MqttClient):
        Logger().setup("Disk monitor", mqtt_client)
        self.folder = folder
        self.mqtt_client = mqtt_client

    def device_event(self, action, device):
        if action == 'add':
            if device.device_type == "partition":                
                if device.get('ID_FS_LABEL'):
                    mount_point = device.device_node
                    disk_name = device.get('ID_FS_LABEL')
                    Logger().info("USB Device connected. Partition detected: {} with name {}".format(mount_point, disk_name), "Disk monitor")
                    self.disks[mount_point] = disk_name

                    payload = NotificationFactory.create_notification_disk_state(disk_name, "connected")
                    self.mqtt_client.publish(Topics.DISK_STATE, payload)
        elif action == 'remove':
            if device.device_type == "partition":
                mount_point = device.device_node
                if mount_point in self.disks:
                    Logger().info("USB Device disconnected on {}".format(device.device_node), "Disk monitor")
                    disk_name = self.disks.pop(mount_point)

                    payload = NotificationFactory.create_notification_disk_state(disk_name, "disconnected")
                    self.mqtt_client.publish(Topics.DISK_STATE, payload)

    def start(self):
        Logger().debug("Starting disks monitoring on mount point {}".format(self.folder), "Disk monitor")

        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='block')        

        for device in iter(monitor.poll, None):
            self.device_event(device.action, device)
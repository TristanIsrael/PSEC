# Analyse technique

Ce document contient des analyses sur les techiques et technologies à mettre en oeuvre pour atteindre certains objectifs métier.

## Objectifs

Les objectifs suivants doivent être analysés :
- Journalisation d'événements depuis un DomU
- Supervision 
    - Etat des composants logiciels du système (services middleware, API, etc)
    - Etat des composants physiques et métriques (queue IO, CPU, RAM, etc)
- Commandes au Dom0
    - Redémarrage du système
    - Redémarrage d'un DomU
    - Configuration d'une VM (ajout d'un partage P9, etc)
- Commandes fichiers
    - Liste des supports USB connectés
    - Liste des fichiers d'un support
    - Copie de fichier
    - Lecture de fichier
    - Création d'un conteneur chiffré
    - Archivage sécurisé d'un fichier
- Interfaces homme-machine
    - Position de la souris
    - Etat des boutons de la souris
    - Position du toucher tactile
    - Etat des touches du clavier
    - Etat des boutons spéciaux (tablettes tactiles)
    - Clavier virtuel (hors MVP)
- Capteurs physiques
    - Luminosité ambiante
    - Charge de la batterie
    - Etat de l'alimentation secteur
- RPC
    - Echange de messages métier entre DomU
    - Notifications / acquittements entre DomU

## Techniques mises en oeuvre

Les objectifs énumérés peuvent être mis en oeuvre avec les techniques suivantes :

| Objectif                  | Direction     | Catégorie     | Techniques | 
|----|----|----|----|
| Journalisation            | DomU -> DomU  | Messages      | pv channel |
| Supervision logiciels     | Dom0 -> DomU  | Etats         | XenStore  |
|                           | DomU -> DomU  | Etats         | XenStore  |
| Supervision matérielle    | à analyser    |               |  |
| Commandes au Dom0         | DomU -> Dom0  | Messages      | pv channel |
| Commmandes fichiers       | DomU -> DomU  | Messages et 9P| pv channel et 9pfs |
| Interfaces homme-machine  | DomU -> DomU  | Messages      | pv channel |
| Capteurs physiques        | Dom0 -> DomU  | Etats         | XenStore  |
| RPC                       | DomU -> DomU  | Messages      | pv channel |

### XenStore

Le XenStore est une base données à accès contrôlé permettant de créer des enregistrement de type clé-valeur. Elle est accessible à la fois par le Dom0 et les DomU, selon les règles d'accès définies à la configuration (cf `xenstore-chmod`).

Depuis le DomO le XenStore est accessible au travers de la socket Unix `/var/run/xenstored/socket`.
Depuis les DomU il faut passer par le Xenbus `/dev/xen/xenbus`, avec une API du type `pyxs`.

### PV channel

Le PV channel est un canal de données bidirectionnel de pair-à-pair du type série permettant d'échanger des données entre le Dom0 et les DomU ainsi qu'entre les DomU.

La configuration du DomU est faite grâce au paramètre suivant :
```
channel = [ name=nom_du_canal, connection=socket, path=chemin_de_la_socket backend=numero_du_domaine ]
```

Sur le Dom0, le canal est accessible sur la socket Unix définie dans le paramètre `path`.
Sur le DomU, le canal est accessible sur la socket `/dev/hvc[1-9]`. Le canal `0` est réservé à la console du DomU, le premier canal auxiliaire créé aura l'identifiant `hvc1`.

Le paramètre `backend` peut être utilisé pour créer un canal avec un DomU directement.

### 9pfs

Le protocole Plan9 est pris en charge par Xen grâce au protocole 9p et au driver backend/frontend utilisant le XenBus pour réaliser des montages de systèmes de fichiers distants, sur le Dom0 ou un DomU.

La configuration du DomU est grâce au paramétrage suivant :
```
p9 = [
	"tag=nom_du_tag_P9, path=chemin_du_partage, backend=_numero_du_domaine, security_model=none"
]
```

Dans le DomU, le montage est réalisé grâce à la commande suivante :
```
# mount -t 9p -o trans=xen,version=9p2000.L nom_du_tag_P9 chemin_du_point_de_montage
```

### Surveillance des supports USB

L'implémentation de 9pfs de Xen ne gère pas les notifications en cas de changement sur les inodes ou sur le système de fichier.

Il est donc nécessaire d'utiliser une technique de polling pour surveiller les fichiers et répertoires du disque.

```
import logging
from watchdog.observers.polling import PollingObserver
from watchdog.events import LoggingEventHandler

logging.basicConfig(level=logging.INFO)
event_handler = LoggingEventHandler()
observer = PollingObserver()
observer.schedule(event_handler, "/chemin/du/dossier", recursive=False)
observer.start()
observer.join()
```

### Stratégie

La stratégie de gestion des supports USB est expliquée dans cette section.

#### Stratégie nominale

Les supports USB sont gérés par le domaine `vm-sys-usb`. 
Ce domaine expose sur le Xenbus avec le driver 9P les répertoires suivants :
- `/mnt/usb/`

Lorsqu'un support USB est connecté, un nouveau point de montage apparaitra dans `/mnt/usb`. Chaque point de montage est préfixé avec un ordre séquentiel d'apparition sur le système :
- `/mnt/usb/1-Maclé`
- `/mnt/usb/2-NO NAME`

Les domaines qui souhaitent accéder directement aux fichiers peuvent créer un lien `9p` avec le domaine `vm-sys-usb` et accéder au contenu du ou des disques montés en tant que sous-répertoire du point de montage `/mnt/usb`.

#### Stratégie dégradée

Les tests actuels montrent un dysfonctionnement lors de l'établissement d'un lien 9P direct entre deux domaines utilisateurs (DomU).

*Aucune stratégie dégradée n'a été identifiée pour l'heure.*

### Cardinalités avec vm-sys-usb

Le domaine `vm-sys-usb` n'est pas visibile de tous les domaines pour des raisons de sécurité. Exposer les fichiers contenus sur un support USB vers d'autres domaines les expose à des risques d'infection.
En conséquence, tous les domaines qui sont connectés directement via le partage 9pfs avec le domaine `vm-sys-usb` sont considérés comme à *risque*.

Afin d'éviter que les domaines métier non techniques (par exemeple le contrôleur ou la GUI) ne soient considérés comme des domaines à risque, un protocole spécifique est mis en oeuvre, permettant entre autres le listing des fichiers d'un support USB ou la copie de fichiers. Ce protocole utilise les mécanismes de la messagerie DomU->Dom0.

## Débogage

### Débogage des sockets pv channel

Côté Dom0 : `# socat UNIX-CONNECT:chemin_de_la_socket -`
Côté DomU : `# tail -f /dev/hvc1` pour lire et `echo "TEST" > /dev/hvc1` pour écrire *(obsolète) `printf du_texte | socat UNIX-CONNECT:/dev/hvc1 -` pour écrire*

## Souris et écran tactile

L'objectif est de détecter automatiquement la souris et l'écran tactile sur le système pour les surveiller et exporter leurs états dans le XenStore.

## Versions de noyaux

Les versions des noyaux utilisées par le Dom0 et les DomU doivent être cohérentes.

### Extraction des modules 

Pour extraire les modules du fichier `modloop`, utiliser la commande suivante :
`unsquashfs modloop`

Pour extraire les fichiers initramfs :
`zcat initramfs | cpio -idm`

### Synchronisation Dom0 et DomU

Les objectifs sont :
- avoir des versions de noyaux identiques entre Dom0 et DomU
- avoir des versions de modules correspondant aux noyaux
- éviter les copies de fichiers modules sur les DomU (limiter l'empreinte mémoire)

Pour atteindre ces objectifs, l'organisation est la suivante :
- posséder la dernière version du paquet `linux-lts` sur le Dom0.
- télécharger la dernière version du paquet `linux-virt` sur le Dom0.
  - décompresser le paquet `linux-virt`
  - mettre à disposition le noyau `vmlinuz-virt` pour les DomU
  - créer un modloop `modloop-virt` avec les fichiers du paquet `linux-virt` (`mksquashfs ./lib/modules modloop-virt`)
  - mettre à disposition le fichier `modloop-virt` pour les DomU
  - décompresser le fichier `initramfs-virt`
    - supprimer les fichiers `/var/lib/modules/*`
    - copier les fichiers `/var/lib/modules/6.6.*` du modloop-virt dans l'initramfs
    - recompresser le fichier `initramfs-virt` avec la commande `find . -print0 | cpio --null -ov --format=newc > initramfs-virt & gzip ./initramfs-virt & mv initramfs-virt.gz initramfs-virt`

### Mise à disposition des modules pour les DomU

Les modules sont fournis grâce à la valeur `modloop=modloop-virt` du paramètre `extra` pour chaque DomU. Cela a pour conséquence de monter le fichier `/boot/modloop-virt` au démarrage du DomU.

Il faut préparer un fichier modloop minimal adapté à chaque type de DomU pour optimiser l'utilisation de la RAM.

```
# mkdir /tmp/modloop
# cp -r /lib/modules /tmp/modloop
# cd /tmp/modloop
# mksquashfs . /boot/modloop-virt
```

La commande `unsquashfs -l /boot/modloop-virt` doit afficher ceci :
```
...
squashfs-root/modules/6.6.14-0-virt/kernel/sound/pci/hda/snd-hda-codec.ko
squashfs-root/modules/6.6.14-0-virt/kernel/sound/pci/hda/snd-hda-intel.ko
squashfs-root/modules/6.6.14-0-virt/kernel/sound/virtio
squashfs-root/modules/6.6.14-0-virt/kernel/sound/virtio/virtio_snd.ko
squashfs-root/modules/6.6.14-0-virt/kernel/virt
squashfs-root/modules/6.6.14-0-virt/kernel/virt/lib
squashfs-root/modules/6.6.14-0-virt/kernel/virt/lib/irqbypass.ko
squashfs-root/modules/6.6.14-0-virt/kernel-suffix
...
```

Autre possibilité : injecter les modules directement dans l'initramfs

```
# mkdir /tmp/initramfs-lts
# cd /tmp/initramfs-lts
# cp /boot/initramfs-lts .
# zcat initramfs-lts | cpio -idm
# cp /lib/modules/[version]/... lib/modules/[version]/...
# rm initramfs-lts
# find . -print0 | cpio --null -ov --format=newc > initramfs-lts
# gzip /boot/initramfs-lts
# mv /boot/initramfs-lts.gz /boot/initramfs-lts
```

### Modules utilisés par les DomU

X ipv6                  716800  14
X simpledrm              16384  0
X drm_shmem_helper       28672  1 simpledrm
X drm_kms_helper        266240  1 simpledrm
X syscopyarea            12288  1 drm_kms_helper
X sysfillrect            12288  1 drm_kms_helper
X sysimgblt              12288  1 drm_kms_helper
X fb_sys_fops            12288  1 drm_kms_helper
X drm                   774144  3 drm_kms_helper,drm_shmem_helper,simpledrm
X i2c_core              126976  2 drm_kms_helper,drm
X drm_panel_orientation_quirks    24576  1 drm
X fb                    135168  1 drm_kms_helper
X fbdev                  12288  1 fb
ext4,crc16,crc32c_generic,mbcache,jbd2,squashfs,loop,9p,9pnet,9pnet_xen,netfs,fscache

## PCI passthru

```
# echo 0000:00:04.0 > /sys/bus/pci/devices/0000:00:04.0/driver/unbind
# echo 0000:00:04.0 > /sys/bus/pci/drivers/pciback/new_slot
# echo 0000:00:04.0 > /sys/bus/pci/drivers/pciback/bind
# xl pci-assignable-add "00:04.0"
```

### Udev

Les supports USB sont détectés automatiquement par udev/mdev sur la VM `vm-sys-usb`. udev détecte l'ajout du périphérique et recherche une règle compatible dans le dossier `/etc/udev/rules.d`.
Dans ce dossier doit être placé le fichier `99-usbdisk.rules` appartenenant au projet.

Ce fichier contient les règles suivantes :
`ENV{ID_FS_USAGE}=="filesystem|other|crypto", ENV{ID_FS_LABEL_ENC}=="?*", RUN+="/usr/local/panoptiscan/scripts/mdev-usb-storage"`

### Notes

Pour recharger les règles de udev : `udevadm control --reload-rules`
Pour exécuter les règles : `udevadm trigger`
Pour vérifier que udev a détecté un périphérique : `udevadm info --name /dev/sda1 --query all`
Pour tester l'exécution des règles : `udevadm test /dev/sda1`
Pour observer les règles : `udevadm monitor`

Environnement lors de la connexion d'une clé USB :
```
ID_BUS=usb
DEVNAME=/dev/sda1
ACTION=add
SHLVL=1
ID_SERIAL_SHORT=1-0000:00:03.0-4.1
SEQNUM=3229
USEC_INITIALIZED=4374446177
ID_PART_ENTRY_SIZE=16777184
ID_USB_DRIVER=usb-storage
ID_FS_UUID_ENC=6f5209d3-5e99-4a33-b531-6c52b4e4f5ef
ID_TYPE=disk
MAJOR=8
ID_FS_LABEL_ENC=Transfert
ID_INSTANCE=0:0
DEVPATH=/devices/pci-0/pci0000:00/0000:00:00.0/usb1/1-4/1-4.1/1-4.1:1.0/host0/target0:0:0/0:0:0:0/block/sda/sda1
ID_FS_UUID=6f5209d3-5e99-4a33-b531-6c52b4e4f5ef
ID_PART_TABLE_TYPE=dos
ID_PART_ENTRY_SCHEME=dos
ID_FS_LABEL=Transfert
ID_MODEL_ENC=QEMU\x20HARDDISK\x20\x20\x20
ID_PART_ENTRY_TYPE=0x83
ID_USB_INTERFACES=:080650:
ID_FS_VERSION=1.0
ID_MODEL=QEMU_HARDDISK
DEVLINKS=/dev/disk/by-id/usb-QEMU_QEMU_HARDDISK_1-0000:00:03.0-4.1-0:0-part1 /dev/disk/by-label/Transfert /dev/disk/by-path/xen-pci-0-pci-0000:00:00.0-usb-0:4.1:1.0-scsi-0:0:0:0-part1 /dev/disk/by-uuid/6f5209d3-5e99-4a33-b531-6c52b4e4f5ef
ID_SERIAL=QEMU_QEMU_HARDDISK_1-0000:00:03.0-4.1-0:0
SUBSYSTEM=block
ID_MODEL_ID=0001
DISKSEQ=16
MINOR=1
ID_FS_TYPE=ext4
ID_PATH=xen-pci-0-pci-0000:00:00.0-usb-0:4.1:1.0-scsi-0:0:0:0
ID_VENDOR_ENC=QEMU\x20\x20\x20\x20
ID_PATH_TAG=xen-pci-0-pci-0000_00_00_0-usb-0_4_1_1_0-scsi-0_0_0_0
PARTN=1
ID_PART_ENTRY_DISK=8:0
ID_PART_ENTRY_OFFSET=32
ID_VENDOR=QEMU
PWD=/
DEVTYPE=partition
ID_PART_ENTRY_NUMBER=1
ID_USB_INTERFACE_NUM=00
ID_VENDOR_ID=46f4
ID_FS_USAGE=filesystem
ID_REVISION=2.5+
```

Le libellé du disque est contenu dans la variable `ID_FS_LABEL_ENC` et le système de fichier dans la variable `ID_FS_TYPE`.

Contenu du fichier mdev-usb-storage :
```
#!/bin/sh

LIBELLE=$ID_FS_LABEL_ENC
FS=$ID_FS_TYPE
POINT_MONTAGE=/media/usb/$LIBELLE
PERIPHERIQUE=$DEVNAME
JOURNAL=/var/log/panoptiscan/udev.log

echo "Action : $ACTION" >> /var/log/panoptiscan/udev.log

if [ "$ACTION" == "add" ]
then
        echo "Montage de la partition $LIBELLE avec le systeme de fichier $FS dans $POINT_MONTAGE" >> $JOURNAL
        echo mount $PERIPHERIQUE $POINT_MONTAGE >> $JOURNAL
        mkdir -p $POINT_MONTAGE
        mount $PERIPHERIQUE $POINT_MONTAGE

        echo "Envoi de la notification aux DomU" >> $JOURNAL

fi

if [ "$ACTION" == "remove" ]
then
        echo "Demontage de $POINT_MONTAGE" >> $JOURNAL
        umount $POINT_MONTAGE
        rmdir $POINT_MONTAGE

        echo "Envoi de la notification aux DomU" >> $JOURNAL
fi
```

# IOMMU

Ajouter `iommu=soft` si le matériel ne supporte pas l'IOMMU.
Il faut utiliser de préférence IOMMU (VT-d sous Intel) et HVM pour plus de sécurité.
Pour rendre l'utilisation de l'IOMMU obligatoire (ne pas booter si l'IOMMU n'est pas disponible ou activé), utiliser `iommu=required`.

Pour vérifier si l'IOMMU est activé sur l'hôte : `dmesg | grep -e DMAR -e IOMMU`

# GRUB et UEFI

S'il manque l'entrée Xen dans le menu Grub, il faut renommer le fichier /boot/vmlinuz-lts pour que son nom coincide avec celui de config*. D'autre part, le fichier config peut ne pas être correctement nommé. Si le nom est différent de config-lts, créer un raccourci nommé config-lts.

# Machine virtuelle QEMU

Si le système est utilisé au sein d'une machine virtuelle fournie par QEMU, il faut qu'elle prenne en charge l'IOMMU et VT-d.

Il faut donc que la ligne de commande de qemu contienne les éléments suivants :
```
-cpu ..., +vmx
-device intel-iommu
```

# Bug Grub sur Alpine 3.20

Après l'installation de XEN grub n'affiche pas d'entrée pour Xen. Il faut créer un lien symbolique de `/boot/vmlinuz-lts` vers `/boot/vmlinuz-6.6.32-0-lts`.

# Problème de boot sur la tablette Getax UX10

Le noyau XEN démarre mais au moment de booter le dom0 la machine redémarre.
La solution est de reprendre la configuration Grub de la clé USB d'installation :
- insérer la clé USB d'installation
- monter la partition boot dans `/media/usb`
- sauvegarder le fichier `/boot/grub/grub.cfg`
- copier le fichier `/media/usb/boot/grub/grub.cfg` dans `/boot/grub`
- éditer le fichier `/boot/grub/grub.cfg` et ajouter les paramètres `root` et `rootfstype` avec les valeurs contenues dans le fichier `/boot/grub/grub.cfg` initial.
- ne pas exécuter `update-grub`
- redémarrer.

# Performances

## Partage de fichiers entre VM (dépôt)

Dans l'idéal, les fichiers sont accessibles depuis n'importe quelle VM directement sur le support USB connecté sur `sys-usb`. Or à l'heure actuelle, le partage de fichiers entre VM ne fonctionne pas (problème de configuration ?).

La stratégie actuellement mise en oeuvre consiste à copier le fichier dans un dépôt local avant de l'analyser.
Les avantages et inconvénients sont les suivants :
- (+) les fichiers de la clé ne peuvent pas être modifiés accidentellement par un processus métier
- (-) la copie du fichier dans le dépôt induit une latence dans le processus
  - *ce point doit faire l'objet d'une analyse comparative pour mesurer la latence*
- (-) la copie du fichier dans le dépôt diminue la RAM disponible.
- (-) le partage 9P ne permet pas de protéger les fichiers contre les modifications ni contre la corruption.

Le dépôt doit :
- permettre de partager des fichiers entre machines virtuelles.
- être rapide.
- protéger les fichiers contre les modifications et la corruption, une fois le fichier écrit il ne doit plus être modifié.

Pour améliorer les performances, une piste consiste à remplacer le partage de fichier 9P actuel par un partage de fichier du type disque. Pour ce faire, créer un fichier `raw` sur le dom0 et l'ajouter dans la configuration des VM :
`disk = [ 'file:/chemin/du/fichier.raw,xvda,w!' ]`. L'utilisation du `!` est critique pour permettre un partage du fichier entre VM.

Avantages et inconvénients :
- (+) Le Dom0 n'a plus la possibilité d'accéder directement aux fichiers, ce qui réduit la surface d'attaque.

**La gestion de la concurrence est à la charge du sous-système métier**. *Voir si le socle peut proposer des mécanismes, notamment en fournissant des notifications*.

## GPU Intel HDU Graphics (iGPU)

pris en charge par le module i915 mais avec un problème à GVT-d : https://events.static.linuxfound.org/sites/events/files/slides/XenGT-Xen%20Summit-REWRITE%203RD%20v4.pdf

- https://blog.tmm.cx/2020/05/15/passing-an-intel-gpu-to-a-linux-kvm-virtual-machine/
- https://github.com/intel/gvt-linux/wiki/GVTg_Setup_Guide 

Les modules suivants doivent être disponibles sur le Dom0 : `kvmgt`, `i915`, `vfio`, `mdev`, `kvm`, `drm`, `drm_kms_helper`, `video`, `drm_display_helper`, `ttm`, `intel-gtt`, `hwmon`, `drm_buddy`, `cec`, `i2c-algo-bit`.

Résumé : 
- Configurer la ligne de commande du noyau
- Charger les modules `kvmgt`, `vfio-iommu-type1`, `vfio-mdev`.
- Créer un GPU virtuel.
- ...

**Si l'une des étapes ne fonctionne pas, il est peut-être nécessaire de compiler les modules manquants. Cf sections suivantes.**

### Configuration du noyau

Editer le fichier `/etc/default/grub` et ajouter les options suivantes à la fin de la ligne `GRUB_CMDLINE_LINUX_DEFAULT` :
```
i915.enable_gvt=1 i915.enable_fbc=0
```

*Note : l'option `intel_iommu=1` doit rester présente*

Exécuter la commande `$ sudo update-grub`.

### Chargement automatique des modules

Editer le fichier `/etc/modules-load.d/gvt.conf` avec le contenu suivant :
```
kvmgt
vfio-iommu-type1
vfio-mdev
```

### Création d'un GPU virtuel

Vérifier la présence du répertoire `/sys/bus/pci/devices/0000:00:02.0/mdev_supported_types`.
En cas d'absence, vérifier les options du noyau et redémarrer.

Générer un UUID avec la commande `$ uuidgen`. Exemple : `255a5189-28b0-4ae5-81e8-782f33891d97`.

Créer un GPU virtuel avec la commande `echo (uuid) | sudo tee mdev_supported_types/i915-GVTg_V5_8/create`. *Note : Remplacer (uuid) par l'UUID généré par la précédente commande*.

### Compilation du module kvmgt (si nécessaire)

```
$ git clone https://github.com/alpinelinux/aports.git
$ cd aports
$ git switch 3.19-stable
$ abuild checksum
$ abuild deps
$ abuild unpack
$ abuild prepare
$ abuild build
```

Laisser se dérouler la compilation du noyau (pendant plusieurs heures)/

Modifier le fichier `src/build-lts.x86_64/.config` :
```
CONFIG_DRM_I915_GVT_KVMGT=m
```

Poursuivre avec :

```
$ cd src/build-lts.x86_64
$ make modules
$ sudo cp -r /var/lib/modules/6.6.32-0-lts /var/lib/modules/6.6.32-0-lts.orig
$ sudo make modules_install
$ sudo depmod -a
```

Le noyau est disponible à l'emplacement `src/build-lts.x86_64/arch/x86/boot/bzImage`.
En cas de remplacement du noyau, taper la commande `$ sudo cp src/build-lts.x86_64/arch/x86/boot/bzImage /boot/vmlinuz-6.6.32-0-lts`. Modifie le fichier `grub.cfg` en conséquence.

### Mise à jour de l'initramfs

```
$ sudo cp /boot/initramfs-lts /boot/initramfs-lts.orig
$ sudo mkinitfs -c /etc/mkinitfs/mkinitfs.conf 6.6.32-0-lts
```

Mettre à jour le fichier `grub.cfg` en conséquence.

## Affichage

Sur tablette, il peut être nécessaire de faire pivoter l'affichage. Pour ce faire, ajouter `fbcon=rotate:1` sur la ligne de commande grub.

## Reverse-engineering Qubes OS

Version : 4.2.3
Matériel : Durabook R8

## GRUB

```

multiboot2  /xen-4.17.4.gz placeholder console=none dom0_mem=min:1024M dom0_mem=max:4096M ucode=scan smt=off gnttab_max_frames=2048 gnttab_max_maptrack_frames=4096 
module2    /vmlinuz-6.6.48-1.qubes.fc37.x86_64 placeholder root=... ro rd.luks.uuid=luks... rd.lvm.lv=... plymouth.ignore-serial-consoles 6.6.48-1.qubes.fc37.x86_64 x86_64 rghb quiet usbcore.authorized_default=0
module2 --nounzip /initramfs...

```

## Redirection du flux graphique

L'objectif est de rediriger le flux graphique du serveur VNC de l'application au travers du canal série du DomU.

### Simuler le canal série

`socat PTY,link=/dev/ttyV0,raw,echo=0 PTY,link=/dev/ttyV1,raw,echo=0`

### Rediriger le flux VNC dans le canal série

`socat TCP:localhost:5900 /dev/ttyV0,raw,echo=0`

### Rediriger le flux du canal série vers le client VNC

`socat /dev/ttyV1,raw,echo=0 TCP-LISTEN:5901,reuseaddr,fork`


## Affichage écran DomU

### Méthode VNC

- Installer un serveur X léger : `apk add xserver-xorg xrandr`
- Faire tourner l'écran (tactile) : `DISPLAY=:0 xrandr --output DSI-1 --rotate left`
- Installer un client vnc : `apk add tigervnc-client`
- Se connecter à la VM en plein écran : `DISPLAY=:0 vncviewer :0 -fullscreen`

### Méthode SPICE + QXL

- Installer un serveur X léger : `apk add xserver-xorg xrandr`
- Faire tourner l'écran (tactile) : `DISPLAY=:0 xrandr --output DSI-1 --rotate left`
- Installer un client SPICE : `apk add virt-viewer`
- Ajouter l'affichage au DomU : 
```
vga = "qxl"
videoram = 128
device_model_args = [
    '-spice', 'unix=on,addr=/var/run/spice.sock,disable-ticketing=on,ipv4=off,ipv6=off,image-compression=off',
    '-full-screen'
]
```
- Démarrer le DomU
- Démarrer le client SPICE : `DISPLAY=:0 remote-viewer spice+unix:///tmp/spice.sock`


```
--title=Saphir
--spice-disable-effects=all
--spice-color-depth=32
--spice-disable-audio
```

Changer la résolution dans le DomU :
- Démarrer un serveur X
- Démarrer spice-agentd ? -> a priori pas nécessaire
- `xrandr --output Virtual-1 --display :0 --mode 1280x800`

En automatique (fichier /etc/X11/xorg.conf.d/resolution.conf)
```
Section "Monitor"
    Identifier   "Monitor0"
    Option       "PreferredMode" "1280x800"
EndSection

Section "Screen"
    Identifier "Screen0"
    Monitor    "Monitor0"
    DefaultDepth 24
    SubSection "Display"
        Modes       "1280x800"
    EndSubSection
EndSection

```

https://stafwag.github.io/blog/blog/2018/04/22/high-screen-resolution-on-a-kvm-virtual-machine-with-qxl/

### Méthode SDL

- Installer un serveur X léger : `apk add xserver-xorg xrandr`
- Faire tourner l'écran (tactile) : `DISPLAY=:0 xrandr --output DSI-1 --rotate left`

*à essayer* : `vfb = [ 'sdl=1' ]`* -> Affichage incorrect

### Méthode GTK

```
vga = "stdvga"
device_model_override = "/usr/lib/psec/packages/dist/install/usr/lib/xen/bin/qemu-system-i386"
qemu_env = ['LD_LIBRARY_PATH=/usr/lib/psec/packages/dist/install/usr/lib/'] 
device_model_args = [
     '-display', 'gtk,show-tabs=off,show-cursor=off,window-close=off,show-menubar=off',
]
acpi=0
usb=0
vif=[]
```

## Notes diverses

Désactiver l'économie d'énergie

## Ajouter le support de GTK+ et SDL dans QEMU Xen

Dépendances : `sdl2-dev, gtk+3.0-dev, sdl2_image-dev`

```
$ git clone https://gitlab.alpinelinux.org/alpine/aports.git
$ cd aports
$ cd main/xen/
$ abuild -rK
$ cd src/tools/qemu-xen
$ ./configure --enable-gtk --enable-sdl --enable-sdl-image
```

## Affichage accéléré 2D/3D

Sur le Dom0 :
- installer  qemu-hw-display-virtio-gpu-pci-gl, qemu-ui-gtk, qemu-ui-opengl et virglrenderer

Configurer le DomU :
```
device_model_override = "/usr/bin/qemu-system-x86_64"
device_model_version = "qemu-xen"
device_model_args = [
     '-device', 'virtio-gpu-gl',
     '-display', 'gtk,show-tabs=off,show-cursor=off,window-close=off,show-menubar=off,gl=on'
]
vnc=0
```

Sur le DomU, installer le mode `virtio-gpu` et.
Installer également les drivers opengl.

Performances :
- device virtio-gpu-pci, display gtk,gl=off : 415 fps. 110 en plein écran.
- device virtio-gpu-pci, display gtk,gl=on : 250 fps. 113 en plein écran.

### Drivers graphiques sous QEMU

https://www.kraxel.org/blog/2019/09/display-devices-in-qemu/

- Préferer vhost-user virtio pour la sécurité
- sinon Virtio-gpu (qemu: -device virtio-gpu-pci)
  - This device has (optional) hardware-assisted opengl acceleration support. This can be enabled using the virgl=on property, which in turn needs opengl support enabled (gl=on) in the qemu display.

## Mosquitto

Démarrer Mosquitto sur macOS : `mosquitto -c ~/mosquitto-multiple.conf`

## Débogage sur port série

Vous voulez :

- Vous connecter physiquement via un câble USB-série depuis un PC vers un DomU (par exemple sys-usb, qui capte le port /dev/ttyUSB0) ;
- Et que ce DomU redirige le flux série (entrée/sortie) vers un shell vivant dans le Dom0, de façon totalement transparente et interactive ;
- Donc le terminal ouvert sur /dev/ttyUSB0 côté PC, via minicom, devrait afficher un shell du Dom0, pas du DomU.

Autrement dit :

📦 PC → (USB série) → DomU → (virtio/pvchannel) → Dom0 shell

⸻

✅ Solution : Tunnel série ↔ shell Dom0 via virtio-serial

Vous pouvez parfaitement réaliser cela avec :
 1.	Un DomU (sys-usb) qui lit et écrit vers /dev/ttyUSB0 (port série physique) ;
 2.	Un canal virtio-série entre ce DomU et le Dom0, qui transporte les données de manière bidirectionnelle ;
 3.	Un getty sur le Dom0 branché à ce canal, pour offrir un vrai shell du Dom0.

### Étapes détaillées

🔹 1. Dans le DomU (sys-usb) : capture du port série USB

Le périphérique physique (vu depuis le DomU) est probablement /dev/ttyUSB0.
Vous devez transférer le flux série à travers le canal vers Dom0 :

Lancer un relais :
```
socat /dev/ttyUSB0,raw,echo=0 \
      /dev/vport0p1,raw,echo=0
```

Cela relie le port série physique au canal virtio connecté au Dom0.

Alternative : script Python si vous voulez gérer des détails (ex : login binaire, séquences d’échappement).

⸻

🔹 2. Dans la config Xen du DomU : canal virtio-série

Ajoutez dans la config de sys-usb :
```
device_model_args_hvm = [
  "-chardev", "socket,id=fromusb,path=/tmp/dom0shell,server,nowait",
  "-device", "virtserialport,chardev=fromusb,name=com.relay.shell"
]
```

Cela crée dans Dom0 le socket /tmp/dom0shell.

⸻

🔹 3. Dans le Dom0 : fournir un shell sur le socket

Option simple : agetty directement sur le socket
```
agetty -L -8 115200 /tmp/dom0shell
```

⚠️ Cela fonctionne uniquement si agetty accepte un Unix socket (ce n’est pas toujours le cas). Sinon :

Option propre : créer un pseudotty avec socat ou ncat :
```
socat UNIX-CONNECT:/tmp/dom0shell PTY,link=/dev/pts/dom0shell,raw,echo=0
```

Puis :
```
agetty -L -8 115200 /dev/pts/dom0shell vt100
```

🔹 4. Depuis votre PC

Lancez un terminal série classique :
```
minicom -D /dev/ttyUSB0
```

Vous obtenez alors un shell du Dom0, via un tunnel DomU ↔ Dom0.
Pour vous, cela se comporte comme si le Dom0 était directement relié au port série.

⸻

✅ Résultat
| Etape | Action | 
|--|--|
| PC | Envoie des caractères sur /dev/ttyUSB0 |
| DomU (sys-usb) | Relaye /dev/ttyUSB0 à /dev/vport0p1 |
| Dom0 | Reçoit via /tmp/dom0shell -> agetty |


🔐 Sécurité et robustesse
	•	Vous pouvez restreindre le shell à un utilisateur non-root dans agetty.
	•	Utilisez systemd ou supervisord pour relancer socat/agetty si besoin.
	•	Ajoutez un handshake (par ex. mot de passe en premier) si exposition possible.


## Sortie XL 

`xl info`

```
host                   : saphir.local
release                : 6.12.20-0-lts
version                : #1-Alpine SMP PREEMPT_DYNAMIC 2025-03-24 08:09:11
machine                : x86_64
nr_cpus                : 12
max_cpu_id             : 11
nr_nodes               : 1
cores_per_socket       : 6
threads_per_core       : 2
cpu_mhz                : 1689.603
hw_caps                : bfebfbff:77faf3ff:2c100800:00000121:0000000f:239c27eb:9840078c:00000100
virt_caps              : pv hvm hvm_directio pv_directio hap shadow iommu_hap_pt_share vmtrace gnttab-v1 gnttab-v2
total_memory           : 7933
free_memory            : 2341
sharing_freed_memory   : 0
sharing_used_memory    : 0
outstanding_claims     : 0
free_cpus              : 0
xen_major              : 4
xen_minor              : 19
xen_extra              : .1
xen_version            : 4.19.1
xen_caps               : xen-3.0-x86_64 hvm-3.0-x86_32 hvm-3.0-x86_32p hvm-3.0-x86_64
xen_scheduler          : credit2
xen_pagesize           : 4096
platform_params        : virt_start=0xffff800000000000
xen_changeset          :
xen_commandline        : placeholder loglevel=0 console=null dom0_mem=512M,max:1024M no-real-mode edd=off
cc_compiler            : gcc (Alpine 14.2.0) 14.2.0
cc_compile_by          : buildozer
cc_compile_domain      :
cc_compile_date        : Thu Dec  5 07:41:26 UTC 2024
build_id               : 15af702fbe87428a0a43890ac319043c8d0ec991
xend_config_format     : 4
```

`xl dmesg`

```
(XEN) parameter "loglevel" unknown!
(XEN) Bad console= option 'null'
 Xen 4.19.1
(XEN) Xen version 4.19.1 (buildozer@) (gcc (Alpine 14.2.0) 14.2.0) debug=n Thu Dec  5 07:41:26 UTC 2024
(XEN) Latest ChangeSet:
(XEN) build-id: 15af702fbe87428a0a43890ac319043c8d0ec991
(XEN) Bootloader: GRUB 2.12
(XEN) Command line: placeholder loglevel=0 console=null dom0_mem=512M,max:1024M no-real-mode edd=off
(XEN) Xen image load base address: 0x56400000
(XEN) Video information:
(XEN)  VGA is graphics mode 800x1280, 32 bpp
(XEN)  VBE/DDC methods: none; EDID transfer time: 0 seconds
(XEN) Disc information:
(XEN)  Found 0 MBR signatures
(XEN)  Found 1 EDD information structures
(XEN) CPU Vendor: Intel, Family 6 (0x6), Model 154 (0x9a), Stepping 4 (raw 000906a4)
(XEN) Enabling Supervisor Shadow Stacks
(XEN) Enabling Indirect Branch Tracking
(XEN)   - IBT disabled in UEFI Runtime Services
(XEN) EFI RAM map:
(XEN)  [0000000000000000, 000000000009dfff] (usable)
(XEN)  [000000000009e000, 000000000009efff] (reserved)
(XEN)  [000000000009f000, 000000000009ffff] (usable)
(XEN)  [00000000000a0000, 00000000000fffff] (reserved)
(XEN)  [0000000000100000, 000000005821cfff] (usable)
(XEN)  [000000005821d000, 000000005b31cfff] (reserved)
(XEN)  [000000005b31d000, 000000005b3f9fff] (ACPI data)
(XEN)  [000000005b3fa000, 000000005b4b9fff] (ACPI NVS)
(XEN)  [000000005b4ba000, 000000005befefff] (reserved)
(XEN)  [000000005beff000, 000000005befffff] (usable)
(XEN)  [000000005bf00000, 0000000061ffffff] (reserved)
(XEN)  [0000000062600000, 00000000627fffff] (reserved)
(XEN)  [0000000063000000, 00000000683fffff] (reserved)
(XEN)  [00000000c0000000, 00000000cfffffff] (reserved)
(XEN)  [00000000fe000000, 00000000fe010fff] (reserved)
(XEN)  [00000000fec00000, 00000000fec00fff] (reserved)
(XEN)  [00000000fed00000, 00000000fed00fff] (reserved)
(XEN)  [00000000fed20000, 00000000fed7ffff] (reserved)
(XEN)  [00000000fee00000, 00000000fee00fff] (reserved)
(XEN)  [00000000ff000000, 00000000ffffffff] (reserved)
(XEN)  [0000000100000000, 0000000297bfffff] (usable)
(XEN) BSP microcode revision: 0x00000430
(XEN) ACPI: RSDP 5B3F9014, 0024 (r2 THOA21)
(XEN) ACPI: XSDT 5B3F8728, 011C (r1 THOA21 THOA21TB  1072009 AMI   1000013)
(XEN) ACPI: FACP 5B3F5000, 0114 (r6 THOA21 THOA21TB  1072009 AMI   1000013)
(XEN) ACPI: DSDT 5B388000, 6CDF7 (r2 THOA21 THOA21TB  1072009 INTL 20200717)
(XEN) ACPI: FACS 5B4B8000, 0040
(XEN) ACPI: SSDT 5B3F6000, 1459 (r2 DptfTb DptfTabl     1000 INTL 20200717)
(XEN) ACPI: FIDT 5B387000, 009C (r1 THOA21 THOA21TB  1072009 AMI     10013)
(XEN) ACPI: MSDM 5B386000, 0055 (r3 THOA21 THOA21TB  1072009 AMI   1000013)
(XEN) ACPI: SLIC 5B385000, 0176 (r1 THOA21 THOA21TB  1072009 AMI   1000013)
(XEN) ACPI: SSDT 5B384000, 038C (r2 PmaxDv Pmax_Dev        1 INTL 20200717)
(XEN) ACPI: SSDT 5B37E000, 5D0B (r2 CpuRef  CpuSsdt     3000 INTL 20200717)
(XEN) ACPI: SSDT 5B37B000, 2AA1 (r2 SaSsdt  SaSsdt      3000 INTL 20200717)
(XEN) ACPI: SSDT 5B377000, 33D3 (r2 INTEL  IgfxSsdt     3000 INTL 20200717)
(XEN) ACPI: SSDT 5B369000, D39F (r2 INTEL  TcssSsdt     1000 INTL 20200717)
(XEN) ACPI: HPET 5B368000, 0038 (r1 THOA21 THOA21TB  1072009 AMI   1000013)
(XEN) ACPI: APIC 5B367000, 01DC (r5 THOA21 THOA21TB  1072009 AMI   1000013)
(XEN) ACPI: MCFG 5B366000, 003C (r1 THOA21 THOA21TB  1072009 AMI   1000013)
(XEN) ACPI: SSDT 5B364000, 1F1A (r2 THOA21 Ther_Rvp     1000 INTL 20200717)
(XEN) ACPI: UEFI 5B43D000, 0048 (r1 THOA21 THOA21TB  1072009 AMI   1000013)
(XEN) ACPI: NHLT 5B363000, 002D (r0 THOA21 THOA21TB  1072009 AMI   1000013)
(XEN) ACPI: LPIT 5B362000, 00CC (r1 THOA21 THOA21TB  1072009 AMI   1000013)
(XEN) ACPI: SSDT 5B35E000, 2A83 (r2 THOA21 PtidDevc     1000 INTL 20200717)
(XEN) ACPI: SSDT 5B35B000, 2357 (r2 THOA21 TbtTypeC        0 INTL 20200717)
(XEN) ACPI: DBGP 5B35A000, 0034 (r1 THOA21 THOA21TB  1072009 AMI   1000013)
(XEN) ACPI: DBG2 5B359000, 0054 (r0 THOA21 THOA21TB  1072009 AMI   1000013)
(XEN) ACPI: SSDT 5B357000, 110B (r2 THOA21 UsbCTabl     1000 INTL 20200717)
(XEN) ACPI: DMAR 5B356000, 0088 (r2 INTEL  EDK2            2       1000013)
(XEN) ACPI: SSDT 5B355000, 0571 (r2  INTEL xh_adl_M        0 INTL 20200717)
(XEN) ACPI: SSDT 5B351000, 3AEA (r2 SocGpe  SocGpe      3000 INTL 20200717)
(XEN) ACPI: SSDT 5B34D000, 35A2 (r2 SocCmn  SocCmn      3000 INTL 20200717)
(XEN) ACPI: SSDT 5B34C000, 0144 (r2 Intel  ADebTabl     1000 INTL 20200717)
(XEN) ACPI: ASF! 5B34B000, 0074 (r32 THOA21 THOA21TB  1072009 AMI   1000013)
(XEN) ACPI: PHAT 5B34A000, 0631 (r1 THOA21 THOA21TB        5 MSFT  100000D)
(XEN) ACPI: WSMT 5B361000, 0028 (r1 THOA21 THOA21TB  1072009 AMI     10013)
(XEN) ACPI: FPDT 5B349000, 0044 (r1 THOA21   A M I   1072009 AMI   1000013)
(XEN) System RAM: 7933MB (8124148kB)
(XEN) No NUMA configuration found
(XEN) Faking a node at 0000000000000000-0000000297c00000
(XEN) Domain heap initialised
(XEN) SMBIOS 3.4 present.
(XEN) Using APIC driver default
(XEN) ACPI: PM-Timer IO Port: 0x1808 (24 bits)
(XEN) ACPI: v5 SLEEP INFO: control[0:0], status[0:0]
(XEN) ACPI: SLEEP INFO: pm1x_cnt[1:1804,1:0], pm1x_evt[1:1800,1:0]
(XEN) ACPI: 32/64X FACS address mismatch in FADT - 5b4b8000/0000000000000000, using 32
(XEN) ACPI:             wakeup_vec[5b4b800c], vec_size[20]
(XEN) Overriding APIC driver with bigsmp
(XEN) ACPI: IOAPIC (id[0x02] address[0xfec00000] gsi_base[0])
(XEN) IOAPIC[0]: apic_id 2, version 32, address 0xfec00000, GSI 0-119
(XEN) ACPI: INT_SRC_OVR (bus 0 bus_irq 0 global_irq 2 dfl dfl)
(XEN) ACPI: INT_SRC_OVR (bus 0 bus_irq 9 global_irq 9 high level)
(XEN) ACPI: HPET id: 0x8086a201 base: 0xfed00000
(XEN) PCI: MCFG configuration 0: base c0000000 segment 0000 buses 00 - ff
(XEN) PCI: MCFG area at c0000000 reserved in E820
(XEN) PCI: Using MCFG for segment 0000 bus 00-ff
(XEN) Using ACPI (MADT) for SMP configuration information
(XEN) SMP: Allowing 12 CPUs (0 hotplug CPUs)
(XEN) IRQ limits: 120 GSI, 2376 MSI/MSI-X
(XEN) Switched to APIC driver x2apic_mixed
(XEN) CPU0: invalid PERF_GLOBAL_CTRL: 0 adjusting to 0x3f
(XEN) CPU0: TSC: 38400000 Hz * 88 / 2 = 1689600000 Hz
(XEN) CPU0: bus: 100 MHz base: 1700 MHz max: 4400 MHz
(XEN) CPU0: 400 ... 1700 MHz
(XEN) xstate: size: 0xa88 and states: 0x207
(XEN) CPU0: Intel machine check reporting enabled
(XEN) Unrecognised CPU model 0x9a - assuming vulnerable to LazyFPU
(XEN) Speculative mitigation facilities:
(XEN)   Hardware hints: RDCL_NO EIBRS RRSBA SKIP_L1DFL MDS_NO TAA_NO SBDR_SSDP_NO FBSDP_NO PSDP_NO
(XEN)   Hardware features: IBPB IBRS STIBP SSBD PSFD L1D_FLUSH MD_CLEAR
(XEN)   Compiled-in support: INDIRECT_THUNK SHADOW_PAGING HARDEN_ARRAY HARDEN_BRANCH HARDEN_GUEST_ACCESS HARDEN_LOCK
(XEN)   Xen settings: BTI-Thunk: JMP, SPEC_CTRL: IBRS+ STIBP+ SSBD- PSFD- BHI_DIS_S+, Other: IBPB-ctxt BRANCH_HARDEN
(XEN)   Support for HVM VMs: MSR_SPEC_CTRL MSR_VIRT_SPEC_CTRL RSB EAGER_FPU
(XEN)   Support for PV VMs: MSR_SPEC_CTRL EAGER_FPU
(XEN)   XPTI (64-bit PV only): Dom0 disabled, DomU disabled (with PCID)
(XEN)   PV L1TF shadowing: Dom0 disabled, DomU disabled
(XEN) Using scheduler: SMP Credit Scheduler rev2 (credit2)
(XEN) Initializing Credit2 scheduler
(XEN)  load_precision_shift: 18
(XEN)  load_window_shift: 30
(XEN)  underload_balance_tolerance: 0
(XEN)  overload_balance_tolerance: -3
(XEN)  runqueues arrangement: socket
(XEN)  cap enforcement granularity: 10ms
(XEN) load tracking window length 1073741824 ns
(XEN) Disabling HPET for being unreliable
(XEN) Platform timer is 3.580MHz ACPI PM Timer
(XEN) Detected 1689.603 MHz processor.
(XEN) Freed 1020kB unused BSS memory
(XEN) alt table ffff82d040462998 -> ffff82d040473910
(XEN) Intel VT-d iommu 0 supported page sizes: 4kB, 2MB, 1GB
(XEN) Intel VT-d iommu 1 supported page sizes: 4kB, 2MB, 1GB
(XEN) Intel VT-d Snoop Control not enabled.
(XEN) Intel VT-d Dom0 DMA Passthrough not enabled.
(XEN) Intel VT-d Queued Invalidation enabled.
(XEN) Intel VT-d Interrupt Remapping enabled.
(XEN) Intel VT-d Posted Interrupt not enabled.
(XEN) Intel VT-d Shared EPT tables enabled.
(XEN) I/O virtualisation enabled
(XEN)  - Dom0 mode: Relaxed
(XEN) Interrupt remapping enabled
(XEN) Enabled directed EOI with ioapic_ack_old on!
(XEN) Enabling APIC mode.  Using 1 I/O APICs
(XEN) ENABLING IO-APIC IRQs
(XEN)  -> Using old ACK method
(XEN) ..TIMER: vector=0xF0 apic1=0 pin1=2 apic2=-1 pin2=-1
(XEN) ..no 8254 timer found - trying HPET Legacy Replacement Mode
(XEN) Allocated console ring of 64 KiB.
(XEN) VMX: Supported advanced features:
(XEN)  - APIC MMIO access virtualisation
(XEN)  - APIC TPR shadow
(XEN)  - Extended Page Tables (EPT)
(XEN)  - Virtual-Processor Identifiers (VPID)
(XEN)  - Virtual NMI
(XEN)  - MSR direct-access bitmap
(XEN)  - Unrestricted Guest
(XEN)  - APIC Register Virtualization
(XEN)  - Virtual Interrupt Delivery
(XEN)  - Posted Interrupt Processing
(XEN)  - VMCS shadowing
(XEN)  - VM Functions
(XEN)  - Virtualisation Exceptions
(XEN)  - TSC Scaling
(XEN) HVM: ASIDs enabled.
(XEN) HVM: VMX enabled
(XEN) HVM: Hardware Assisted Paging (HAP) detected
(XEN) HVM: HAP page sizes: 4kB, 2MB, 1GB
(XEN) alt table ffff82d040462998 -> ffff82d040473910
(XEN) altcall: Optimised away 234 endbr64 instructions
(XEN) Brought up 12 CPUs
(XEN) Scheduling granularity: cpu, 1 CPU per sched-resource
(XEN) Initializing Credit2 scheduler
(XEN)  load_precision_shift: 18
(XEN)  load_window_shift: 30
(XEN)  underload_balance_tolerance: 0
(XEN)  overload_balance_tolerance: -3
(XEN)  runqueues arrangement: socket
(XEN)  cap enforcement granularity: 10ms
(XEN) load tracking window length 1073741824 ns
(XEN) Adding cpu 0 to runqueue 0
(XEN)  First cpu on runqueue, activating
(XEN) Adding cpu 1 to runqueue 0
(XEN) Adding cpu 2 to runqueue 0
(XEN) Adding cpu 3 to runqueue 0
(XEN) Adding cpu 4 to runqueue 0
(XEN) Adding cpu 5 to runqueue 0
(XEN) Adding cpu 6 to runqueue 0
(XEN) Adding cpu 7 to runqueue 0
(XEN) Adding cpu 8 to runqueue 1
(XEN)  First cpu on runqueue, activating
(XEN) Adding cpu 9 to runqueue 1
(XEN) Adding cpu 10 to runqueue 1
(XEN) Adding cpu 11 to runqueue 1
(XEN) mcheck_poll: Machine check polling timer started.
(XEN) NX (Execute Disable) protection active
(XEN) d0 has maximum 2496 PIRQs
(XEN) *** Building a PV Dom0 ***
(XEN)  Xen  kernel: 64-bit, lsb
(XEN)  Dom0 kernel: 64-bit, lsb, paddr 0x1000000 -> 0x342c000
(XEN) PHYSICAL MEMORY ARRANGEMENT:
(XEN)  Dom0 alloc.:   0000000288000000->000000028c000000 (110824 pages to be allocated)
(XEN)  Init. ramdisk: 0000000296ce8000->0000000297bffacd
(XEN) VIRTUAL MEMORY ARRANGEMENT:
(XEN)  Loaded kernel: ffffffff81000000->ffffffff8342c000
(XEN)  Phys-Mach map: 0000008000000000->0000008000100000
(XEN)  Start info:    ffffffff8342c000->ffffffff8342c4b8
(XEN)  Page tables:   ffffffff8342d000->ffffffff8344c000
(XEN)  Boot stack:    ffffffff8344c000->ffffffff8344d000
(XEN)  TOTAL:         ffffffff80000000->ffffffff83800000
(XEN)  ENTRY ADDRESS: ffffffff82caa4f0
(XEN) Dom0 has maximum 12 VCPUs
(XEN) Initial low memory virq threshold set at 0x4000 pages.
(XEN) Scrubbing Free RAM in background
(XEN) Std. Loglevel: Errors, warnings and info
(XEN) Guest Loglevel: Nothing (Rate-limited: Errors and warnings)
(XEN) *** Serial input to DOM0 (type 'CTRL-a' three times to switch input)
(XEN) Freed 672kB init memory
```

## virt-host-validate

$ virt-host-validate
  QEMU: Checking for hardware virtualization                                 : PASS
  QEMU: Checking if device '/dev/kvm' exists                                 : PASS
  QEMU: Checking if device '/dev/kvm' is accessible                          : FAIL (Check /dev/kvm is world writable or you are in a group that is allowed to access it)
  QEMU: Checking if device '/dev/vhost-net' exists                           : WARN (Load the 'vhost_net' module to improve performance of virtio networking)
  QEMU: Checking if device '/dev/net/tun' exists                             : FAIL (Load the 'tun' module to enable networking for QEMU guests)
Unable to initialize cgroups: internal error: no cgroup backend available
  QEMU: Checking for device assignment IOMMU support                         : PASS
  QEMU: Checking if IOMMU is enabled by kernel                               : PASS
  QEMU: Checking for secure guest support                                    : WARN (Unknown if this platform has Secure Guest support)
   LXC: Checking for Linux >= 2.6.26                                         : PASS
   LXC: Checking for namespace 'ipc'                                         : PASS
   LXC: Checking for namespace 'mnt'                                         : PASS
   LXC: Checking for namespace 'pid'                                         : PASS
   LXC: Checking for namespace 'uts'                                         : PASS
   LXC: Checking for namespace 'net'                                         : PASS
   LXC: Checking for namespace 'user'                                        : PASS
Unable to initialize cgroups: internal error: no cgroup backend available
   LXC: Checking if device '/sys/fs/fuse/connections' exists                 : FAIL (Load the 'fuse' module to enable /proc/ overrides)
    CH: Checking for hardware virtualization                                 : PASS
    CH: Checking if device '/dev/kvm' exists                                 : PASS
    CH: Checking if device '/dev/kvm' is accessible                          : FAIL (Check /dev/kvm is world writable or you are in a group that is allowed to access it)
saphir:~$

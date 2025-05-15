# Créer une clé USB bootable

Cette procédure décrit le processus de création d'un clé USB bootable.

## Procédure

- Télécharger l'image ISO officielle d'Alpine Standard ([Alpine Standard x86_64](`https://dl-cdn.alpinelinux.org/alpine/v3.21/releases/x86_64/alpine-standard-3.21.3-x86_64.iso`)).
- Copier l'ISO sur une clé USB : `$ sudo dd if=alpine-standard-xxx.iso of=/dev/xxx bs=4m`
- Démarrer sur la clé USB
- S'identifier en tant que `root`
- Taper `# setup-alpine` et configurer le système sans installation sur disque ni stockage de la configuration
  - Le script échouera
- Taper `# apk add dosfstools wipefs`
- Installer la nouvelle clé qui deviendra le système bootable
  - dans `dmesg` identifier la nouvelle clé `sdx`
- Préparer la clé (voir chapitre préparation de la clé bootable)
- Débrancher la clé ISO et ne conserver que la nouvelle clé bootable
- Redémarrer sur la clé bootable
- Configurer les dépôts dans `/etc/apk/repositories`
- Le cas échéant, remonter le système en R/W : `# mount -o remount,rw /dev/sda1 /media/usb`
- Taper `# setup-apkcache /media/usb/cache`
- Taper `# apk cache -v sync`
- Taper `# setup-lbu usb`
- Taper `# lbu commit -d`
- Le système bootable est prêt
  - *Installer les paquets nécessaires à la construction du produit bootable sur USB*
  - La configuration sera réalisée sur le support USB
  - Le cas échéant retirer la configuration du réseau et des dépôts pour un boot plus rapide

### Préparation de la clé bootable

Taper les commandes suivantes pour préparer la clé bootable (remplacer `sdx` par l'identifiant correct):

`wipefs -a /dev/sdx`
```
  fdisk -w always /dev/sdx <<EOF
  o
  n
  p
  1
  2048
  -0
  t
  0c
  a
  w
EOF
```

Formater la clé : `# mkdosfs -F32 /dev/sdx1`

La rendre bootable avec Alpine : `# setup-bootable -vUfs /media/sda /dev/sdx1`, vérifier d'abord si l'image ISO est montée sur `/media/usb` ou `/media/sda` (par exemple)
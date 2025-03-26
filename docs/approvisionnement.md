# Approvisionnement

Ce document présente différentes façons d'approvisionner un équipement avec un système basé sur PSEC.

## Manuel

L'approvisionnement manuel consiste à dérouler un processus d'installation pas-à-pas à partir d'un support USB.

1 - Créer une clé USB d'installation pour Alpine Linux. 
  - La version d'Alpine Linux utilisée doit correspondre à celle du dépôt souhaité.
  - L'image ISO utilisée doit être celle de **Alpine Standard**

2 - Installer Alpine Linux sur l'équipement.
  - Lui affecter un périphérique réseau avec DHCP ou IP fixe en fonction de la situation.
  - Dans la section APK Mirror, si un dépôt Internet est utilisé choisir `f`, sinon ne pas choisir d'entrée de menu mais saisir l'URL du dépôt `main` local d'Alpine.
  - Créer un compte utilisateur `admin`

3 - A la fin de l'installation redémarrer le système

4 - A l'issue du redémarrage, se logger en tant que `admin`

5 - Ajouter les dépôts de binaires 
  - Taper la commande `$ su - root` puis le mot de passe du compte `root`
  - Taper la commande `# vi /etc/apk/repositories` et ajouter le dépôt `community` ainsi que le dépôt `PSEC` et les dépôts spécifiques au produit à installer.
  - Taper `:wq`

6 - Ajouter les clés PGP 
  - Taper la commande `# cd /etc/apk/keys` puis `# wget [URL du depot PSEC]/psec.rsa.pub` et recommencer avec les clés des dépôts spécifiques au produit à installer.
  - Taper la commande `# apk update`

7 - (Optionnel) Autoriser le compte `admin` à exécuter des commandes `root`
  - Taper la commande `# apk add sudo`, puis `# visudo`
  - Editer la ligne `# %wheel ALL=(ALL:ALL) NOPASSWD: ALL` et retirer le `#` au début pour décommenter la ligne.
  - Taper `:wq`  
  - Taper la commande `# exit`

8 - Installer XEN
  - Taper la commande `$ sudo apk add xen xen-hypervisor`
  - Taper la commande `$ sudo reboot`
  - Au redémarrage, séletionner dans GRUB la première entrée contenant le libellé `Xen`

9 - Installer le produit en suivant la documentation fournie.
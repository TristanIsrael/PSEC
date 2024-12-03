# Messagerie

Ce document présente une analyse des besoins relatifs à l'échange de messages à l'intérieur du système, entre domaines.

## MVP

Sur le MVP, la messagerie est basée sur un protocole maison formatté en JSON. Le dictionnaire permet d'émettre des commandes (RPC), des réponses et des notifications.

Sur un DomU, les messages sont échangés sur le port série de messagerie `/dev/hvc2`.
Sur le Dom0, les messages sont échangés sur la socket UNIX `/var/run/vm-*-msg.sock`.

## Besoins

Les *design drivers* du produit incluent notamment l'utilisation exclusive de logiciels et technologies sur étagère. Le MVP ne satisfait pas cette exigence car les contrôleurs permettant l'échange des messages à l'intérieur du système et le protocole en lui-même ne sont pas sur étagère.

## Evolution vers MQTT

Le système de messagerie doit donc évoluer vers des technologies sur étagère prises en charge par des logiciels disponibles dans le dépôt Alpine sans développement complémentaire en dehors du besoin de forger des messages et de les traiter.

MQTT est un protocole de messagerie léger un simple répondant à ces exigences.

Un broker Mosquitto sur le Dom0 permettra de distribuer les messages, y compris au contrôleur sur le Dom0 lui-même. Sur les DomU, le contrôleur de messagerie recevra directement les messages qui sont destinés au DomU.

### Grammaire et dictionnaire

La grammaire ne subira pas d'évolution majeure dans la mesure où les fonctions du système n'évolueront. Seul le transport est modifié.

Les catégories de messages sont :
- Commandes système (disques, stockage local, etc)
- Supervision
- Annonces de services

### Topics

Un *topic* MQTT est un canal de communication spécialisé sur un sujet. Dans PSEC, les *topics* correspondent aux familles de fonctions : fichiers, supervision. Les applications métier sont libres de créer leurs propres topcis.

Le nom du topic contient la commande et la charge utile contient l'identifiant du domaine à qui renvoyer la réponse.

Exemple :
- Le topic `system/disks/list_disks/request` permet à un DomU de demander la liste des disques connectés. Le demandeur indique son identifiant à la fin du topic pour recevoir la réponse : `system/disks/list_disks/response/vm-gui`.

Cela permet une communication *unicast* entre le demandeur et la VM qui va traiter cette demande (à savoir sys-usb) qui va répondre en précisant dans le topic l'identifiant du demandeur à qui la réponse est destinée, mais également une communication *multicast* permettant aux autres VM intéressées par la réponse de la recevoir en s'abonnant au même topic en réduisant le filtrage.

Liste des topics

| Commande MVP | Topic racine* | Payload commande | Description commande | Payload réponse | Description réponse |
|--|--|--|--|--|--|
| TypeCommande.LISTE_DISQUES | `system/disks/list_disks` | `{}` | Demande la liste des disques connectés au système | `{ 'disks': [ { 'label': 'nom', 'id': 'identifier' } ] }` | |
| TypeCommande.LISTE_FICHIERS | `system/disks/list_files` | `{ 'disk': 'identifier' }`| Demande la liste des fichiers d'un disque | `{ 'disk': 'identifier', 'files': [ { 'path': 'path', 'size': 0; 'name': '', 'type': '[file\|folder]' } ] }` | |
| TypeCommande.LIT_FICHIER | `system/disks/read_file` | `{ 'source_disk': 'nom', 'filepath': 'path' }` | Demande la mise à disposition d'un fichier dans le dépôt local | `{ 'status': 'ok\|error' }` | |
| TypeCommande.COPIE_FICHIER | `system/disks/copy_file` | `{ 'source_disk': 'nom', 'filepath': 'path', 'target_disk': 'nom' }` | Demande la copie d'un fichier d'un disque vers un autre | `{ 'status': 'ok\|error' }` | |
| TypeCommande.SUPPRIME_FICHIER | `system/disks/remove_file` | `{ 'disk': 'nom', 'filepath': 'path' }` | Demande la suppression d'un fichier d'un disque | `{ 'status': 'ok\|error' }` | |
| TypeCommande.START_BENCHMARK | `system/misc/benchmark` | `{ 'module': '' }` | Demande le démarrage du processus de calcul des performances du système | `{ 'status': 'started\|error\|finished' }` | | 
| TypeCommande.GET_FILE_FOOTPRINT | `system/disks/get_file_footprint` | `{ 'disk': 'nom', 'filepath': 'path' }` | Demande l'empreinte numérique d'un fichier | `{ 'footprint': 'xxxx' }` | |
| TypeCommande.CREATE_FILE | `system/disks/create_file` | `{ 'disk': 'nom', 'filepath': 'path', 'data': 'contenu' }` | Demande la création d'un fichier sur un disque | `{ 'status': 'ok\|error' }` | |
| TypeCommande.LISTE_COMPOSANTS | `system/components/discover` | `{}` | Demande la liste des composants du système | `{ 'components': [ { 'id': '', 'label': '', 'type': '' } ] }` | L'association entre un composant et le client est faite grâce à l'identifiant fournit dans le suffixe du topic |

(*) la racine du topic doit être complétée par le suffixe de commande (`/request`) ou de réponse (`/response`).

Notes :
- The binary data must be encoded in Base64

Liste des notifications

| Evenement MVP | Topic racine* | Payload notification | Description notification |
|--|--|--|--|
| TypeEvenement.FICHIER | `system/disk/new_file` | `{ 'disk': '', 'filepath': 'path', 'size_in_bytes': 0}` | Indique qu'un nouveau fichier est disponible dans le dépôt local ou sur un disque |
| TypeEvenement.ERREUR | `system/events/error` | `{ 'module':'', 'datetime': '', 'level': 0, 'description'; ''}` | Indique qu'une erreur s'est produite dans un module |

(*) la racine du topic doit être complétée par le suffixe de notification (`/notification`).
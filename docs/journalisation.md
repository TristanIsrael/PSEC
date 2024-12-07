# Journalisation

Ce document présente la stratégie de journalisation et les mécanismes mis en oeuvre.

## Fonctionnalités

La journalisation se situe à deux niveaux :
- système d'exploitation : les services peuvent enregistrer un certain nombre d'événements dans des fichiers situés dans `/var/log` ou transmis à un gestionnaire de journaux comme `syslog`.
- application métier : les applications et le socle produisent des événements concernant le fonctionnement du produit.

Seuls les événements métier sont concernés par cette documentation.

## Architecture

La journalisation utilise la messagerie du système au travers de topics spécifiques `system/events`.

## Niveau de débogage

Le niveau de débogage est défini grâce à la commande `system/events/set_loglevel`.

## Emission d'un événement

Le partage d'une information à journaliser se fait grâce aux notifications `system/events/[loglevel]` où `loglevel` peut être :
- `debug` : Information à des fins de débogage
- `info` : Information générale
- `warn` : Avertissement
- `error` : Erreur logicielle impactant seulement une partie des fonctions du système
- `critical` : Erreur logicielle ou matérielle empêchant le système de fonctionner.

L'émission d'un événement est simplifiée par la classe python `Logger`. Elle s'utilise de la façon suivante :

`Logger().debug("Message de débogage", "Nom du module")` 
ou encore `Logger().info("Message d'information")`.

## Enregistrement

Le socle conserve automatiquement tous les événements d'un niveau supérieur ou égale à celui défini par la commande `set_loglevel` (ou `info` par défaut) dans un fichier qui peut être copié ou téléchargé ensuite à la demande. Le niveau de journalisation peut être défini afin de ne retenir qu'une partie seulement des événements.

## Récupération du journal

La commande permettant de récupérer le journal est `system/events/save_log`.
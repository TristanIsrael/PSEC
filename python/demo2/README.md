# Safecor Demonstration application

## Fonctionnement

Ce projet de démonstration permet de mettre en évidence les mécanismes de communication inter-domaines au sein du socle Safecor.

L'interface graphique fournit un champ de saisie qui permet à l'utilisateur d'entrer un message. Le message sera ensuite envoyé au travers du broker puis reçu par un premier composant qui l'enrichira avant d'émettre une réponse. Cette réponse sera ensuite captée par un deuxième composant qui l'enrichira à son tour.

Afin d'illustrer le fonctionnement des requêtes vers le socle, chaque composant enrichira le message initial avec des éléments issus du système :
- nb_cpu - La quantité de CPU du système.
- is_plugged - vrai si le système est connecté à une alimentation secteur, faux s'il fonctionne sur batterie.

### Commandes et messages

Les `topics` utilisés sont les suivants :

| Topic | Arguments | Description |
|--|--|--|
| `demo/lambda/request` | `{ "message": "le message saisi par l'utilisateur" }` | Le message saisit par l'utilisateur est transmis aux composants du système par ce topic. |
| `demo/lambda/step/#` | `{ "message": "le message saisi par l'utilisateur et enrichi à l'étape #" }` | Le message est suivi par l'un ou l'autre des composants et enrichi puis transmis. |
| `demo/lambda/response` | `{ "result": "le message enrichi final" }` | Le résultat du traitement est retourné au travers de ce message. |

### Composants

Le système de démonstration comporte 3 composants :

| Composant | Rôle | Fichier |
|--|--|--|
| GUI | Affiche l'interface graphique et gère les interactions avec l'utilisateur | `AppController.py` |
| Composant 1 | Premier composant d'enrichissement | `Composant1.py` |
| Composant 2 | Deuxième composant d'enrichissement | `Composant2.py` |

## Dépendances

La construction du paquet wheel nécessite le module python `build` :
```
$ pip install build
```

**Une connexion Internet est nécessaire**

## Construction

```
$ python3 -m build --no-isolation
```


# Panoptiscan

 Panoptiscan

## Use cases à traiter

- Logger les performances et la consommation mémoire en mode DEBUG

- Désacidifier les fichiers sur la station pour les scanne

## Exigences

- La station blanche ne doit pas avoir de périphérique de masse connecté (disque dur, carte mémoire)

- Elle doit être construite à partir d'un master homologué, ce master doit être vérifié

- en cas de détection de virus, ne copier que les fichiers sains

- le journal des scans est copié en même temps que les fichiers

## Pistes envisagées

- Définition d'un master avec YOCTO, facilement modifiable, maîtrisé et déployable -> Sortie au format IMG

## Bug fixes

- OK après l'insertion du support 1 : modifier le message "Insérer une deuxième clé USB"

- après le scan :

- OK cacher la barre de progression

- remonter les chiffres des résultats

- afficher le bouton de copie et le bouton d'éjection côte-à-côte

- ajouter un bouton pour éteindre le dispositif

## Débogage

- https://github.com/pyutils/line_profiler

## Icones

https://iconsplace.com/custom-color/eject-icon-17/

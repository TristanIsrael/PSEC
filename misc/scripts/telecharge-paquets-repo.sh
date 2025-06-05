#!/bin/sh

#WGET_OPTS='-c -N -q -m -p -E -k -K -np -l 1 -nd -e robots=off --show-progress --reject=html,htm'

if [ "$#" -ne 2 ]; then
    echo "Arguments manquant :"
    echo "$0 [x86_64, armv7, aarch64] [version]"
    exit 1
fi

MIRROR_UNC="mirrors.ircam.fr"
MIRROR_ROOT="pub"

REPO_MAIN_ROOT="rsync://$MIRROR_UNC/$MIRROR_ROOT/alpine/v$2/main"
REPO_COMMUNITY_ROOT="rsync://$MIRROR_UNC/$MIRROR_ROOT/alpine/v$2/community"

REPO_MAIN_URL="$REPO_MAIN_ROOT/$1"
REPO_COMMUNITY_URL="$REPO_COMMUNITY_ROOT/$1"

echo "Téléchargement des paquets Alpine v$2 pour l'architecture $1"

mkdir -p alpine/v$2/community/$1
echo "URL $REPO_COMMUNITY_URL"
rsync -avz --delete $REPO_COMMUNITY_URL/ alpine/v$2/community/$1/
#wget $WGET_OPTS -P alpine/v$2/community/$1 $REPO_COMMUNITY_URL

mkdir -p alpine/v$2/main/$1
echo "URL $REPO_MAIN_URL"
rsync -avz --delete $REPO_MAIN_URL/ alpine/v$2/main/$1/
#wget $WGET_OPTS -P alpine/v$2/main/$1 $REPO_MAIN_URL

echo "Téléchargement terminé"
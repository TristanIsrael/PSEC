#!/bin/sh

echo Generate PGP keys

rm -rf /$USER/.abuild

abuild-keygen -nq
ln -s `ls /$USER/.abuild/*-*.rsa.pub` /$USER/.abuild/local.rsa.pub
ln -s `ls /$USER/.abuild/*-*.rsa` /$USER/.abuild/local.rsa

echo Copy PGP keys
cp `ls /$USER/.abuild/*-*.rsa.pub` /etc/apk/keys/local.rsa.pub

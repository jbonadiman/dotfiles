#!/usr/bin/env sh

scripts_path=$(realpath $(dirname $(readlink -f $0)))

source $scripts_path/zsh_functions

if exists waterfox-g4
then
	echo Waterfox already installed, skipping...
else
	git clone https://aur.archlinux.org/waterfox-g4-bin.git /tmp/waterfox
	cd /tmp/waterfox
	makepkg -si --noconfirm

	echo Done!
fi

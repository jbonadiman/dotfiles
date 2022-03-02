#!/usr/bin/env sh

scripts_path=$(realpath $(dirname $(readlink -f $0)))

source $scripts_path/zsh_functions

if exists genie; then
  echo "genie is already installed, skipping..."
  exit 0
fi

echo "Getting genie sources..."
git clone https://aur.archlinux.org/genie-systemd-git.git /tmp/genie-systemd

echo "Installing genie"
(cd /tmp/genie-systemd && makepkg -si)

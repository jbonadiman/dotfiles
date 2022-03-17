#!/usr/bin/env sh

scripts_path=$(realpath $(dirname $(readlink -f $0)))
. $scripts_path/../zsh/utils

if exists n; then
  echo n is already installed, skipping...
  exit 0
fi

echo "Downloading n sources..."
git clone git@github.com:tj/n.git /tmp/n

echo "Using admin privileges to install n..."
sudo make --directory /tmp/n install

echo "Installing node..."
n lts

echo "n was installed successfully!"

#!/usr/bin/env sh

echo "Downloading bat-extras sources..."
git clone https://aur.archlinux.org/bat-extras-git.git /tmp/bat-extras

echo "Installing bat-extras..."
cd /tmp/bat-extras && makepkg -si

echo "bat-extras was installed successfully!"

#!/usr/bin/env sh

echo "Downloading n sources..."
git clone git@github.com:tj/n.git /tmp/n

echo "Using admin privileges to install n..."
sudo make --directory /tmp/n install

echo "n was installed successfully!"

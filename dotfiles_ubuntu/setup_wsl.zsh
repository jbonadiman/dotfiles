#!/usr/bin/env zsh

echo "Starting WSL setup"

if [ -e /etc/wsl.conf ]; then
  echo "Windows paths are already removed from WSL path, skipping..."
else
  echo "Removing Windows paths from WSL path"
  echo "Enter superuser (sudo) password so the file /etc/wsl.conf can be appended"
  echo "[interop]
  enabled=false # default is true
  appendWindowsPath=false # default is true" | sudo tee /etc/wsl.conf
fi

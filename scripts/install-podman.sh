#!/usr/bin/env sh

scripts_path=$(realpath $(dirname $(readlink -f $0)))

source $scripts_path/zsh_functions

if exists podman; then
  echo "podman is already installed, skipping..."
  exit 0
fi

force_rootless=0
# parse arguments
while getopts f: flag; do
  case "${flag}" in
    fix-rootless) fix_rootless=1
  esac
done

if [ fix_rootless ]; then
  shell_config=$(readlink -f "$HOME/.$(basename $SHELL)rc")

  if [ ! grep "alias podman" $shell_config ]; then
    sed -i "1i alias podman=sudo podman" $shell_config
  else
    echo "alias already added to $(basename $shell_config) file. Skipping..."
  fi

  sudoers_file="/etc/sudoers.d/01_podman"
  echo "Requesting admin privileges to read '/etc/sudoers' file..."
  if [ ! -f $sudoers_file ]; then
    echo "Writing '$(whoami) ALL = NOPASSWD: $(which podman | head -n 1)' to $sudoers_file..."
    echo "Rootless fixed!"
  else
    echo "podman sudoers file already exists. Skipping..."
  fi
  exit 0
fi

echo "Sourcing OS information..."
. /etc/os-release

echo "Registering Kubic repository..."
sudo sh -c "echo 'deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/x$(capitalize $ID)_$VERSION_ID/ /' > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list"

echo "Getting Kubic release key..."
wget -nv -q https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable/x$(capitalize $ID)_$VERSION_ID/Release.key -O Release.key

echo "Add Kubic release key to APT keychain..."
sudo apt-key add - < Release.key > /dev/null

echo "Requesting admin privilege to update APT..."
sudo echo > /dev/null

echo "Updating APT repositories..."
sudo apt-get update -qq

echo "Requesting admin privileges to install 'buildah' and 'podman'..."
sudo echo > /dev/null

echo "Installing 'buildah' and 'podman'..."
sudo apt-get -qq -y install buildah podman

echo "Getting podman info..."
podman info

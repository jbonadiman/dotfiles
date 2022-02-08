#!/usr/bin/env sh

capitalize() {
  printf '%s' "$1" | head -c 1 | tr [:lower:] [:upper:]
  printf '%s' "$1" | tail -c '+2'
}

exists() {
  command -v $1 >/dev/null 2>&1
}

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


if exists podman; then
  echo "'podman' is already installed. If you are having any troubles, try performing a clean install or fix rootless!"
  exit 1
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

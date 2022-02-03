#!/usr/bin/env sh

capitalize()
{
  printf '%s' "$1" | head -c 1 | tr [:lower:] [:upper:]
  printf '%s' "$1" | tail -c '+2'
}

exists() {
  command -v $1 >/dev/null 2>&1
}

if exists podman; then
  echo "'podman' is already installed. If you are having any troubles, try performing a clean install!"
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

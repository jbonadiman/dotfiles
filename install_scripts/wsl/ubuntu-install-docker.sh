#!/usr/bin/env sh

if exists docker
then
  echo docker is already installed, skipping...
  exit 0
fi

. /etc/os-release

trap '
  trap - INT # restore default INT handler
  echo "Installation aborted by the user!" >&2
  kill -s INT "$$"
' INT

shell_config=$(readlink -f "$HOME/.$(basename $SHELL)rc")
DOCKER_CFG="/etc/docker"
# DOCKER_DISTRO=$(wsl.exe -l -q | tr -d '\0' | tr '\r\n' ' ' | grep -io $ID)
# DOCKER_DIR="/mnt/wsl/shared-docker"
# DOCKER_SOCK="$DOCKER_DIR/docker.sock"

error() {
  printf "%s\n" "$1" >&2;
  exit $2
}

request_admin() {
  echo requesting admin privileges to $1...
  sudo echo > /dev/null
}

echo "###################################################################################################"
echo "# * This script must be installed on Ubuntu distros. It wasn't tested throughly on many versions,"
echo "# but it's expected to run on 20.04 and 22.04."
echo "##################################################################################################"

read -r -p "Do you want to proceed with the installation? [Y/n] " response
echo

case $response in [yY][eE][sS]|[yY]|[jJ]|'')
  ;;
  *)
  error "Installation aborted by the user!" 2
esac

echo

request_admin "check and uninstall previous docker installations"
echo "Uninstalling previous installations..."
sudo apt-get remove docker-engine > /dev/null
sudo apt-get remove docker.io > /dev/null
sudo apt-get remove containerd > /dev/null
sudo apt-get remove runc > /dev/null
sudo apt-get remove docker > /dev/null

request_admin "install dependencies"
echo "Installing dependencies..."
sudo apt-get install -y -qq --no-install-recommends apt-transport-https ca-certificates curl gnupg2 || ( error "ERROR: Failed to install docker dependencies." 1 )

request_admin "load docker repo keys"
echo "Trusting docker repo..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg || ( error "ERROR: Failed to get or load docker repo key." 1 )

request_admin "register docker repo"
echo "Registering docker repo on apt"
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null|| ( error "ERROR: Failed to register docker repo." 1 )
sudo apt-get update -qq

request_admin "install docker"
echo "Installing docker..."
sudo apt-get -y -qq install docker-ce docker-ce-cli containerd.io docker-compose-plugin || ( error "ERROR: Failed to install docker." 1 )

request_admin "add $USER to docker group"
sudo usermod -aG docker $USER || ( error "ERROR: Failed to add $USER to docker group." 1 )

echo "Docker was installed successfully and a start script was generated. You should invoke it everytime before using docker. You may also add the invocation to your shell rc file, so it gets executed automatically when you login."

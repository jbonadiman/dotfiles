#!/usr/bin/env sh
. /etc/os-release

trap '
  trap - INT # restore default INT handler
  echo "Installation aborted by the user!" >&2
  kill -s INT "$$"
' INT

shell_config=$(readlink -f "$HOME/.$(basename $SHELL)rc")
DOCKER_CFG="/etc/docker"
DOCKER_DISTRO=$(wsl.exe -l -q | tr -d '\0' | tr '\r\n' ' ' | grep -io $ID)
DOCKER_DIR="/mnt/wsl/shared-docker"
DOCKER_SOCK="$DOCKER_DIR/docker.sock"

error() {
  printf "%s\n" "$1" >&2;
  exit $2
}

request_admin() {
  echo "Requesting admin privileges to $1..."
  sudo echo > /dev/null
}

echo "###################################################################################################"
echo "# * This script must be installed in WSL version 2. To make sure you're running the right version,"
echo "# on Windows run the following command: 'wsl --set-default-version 2'."
echo "# * Keep in mind that it was tested and adapted to be used in Ubuntu 20.04. If you're using any"
echo "# other distro, check additional informations here:"
echo "# https://dev.to/bowmanjd/install-docker-on-windows-wsl-without-docker-desktop-34m9/"
echo "# and get in touch so I can update this script."
echo "# * It also assumes the current distro is the default"
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
curl -fsSL https://download.docker.com/linux/${ID}/gpg | sudo apt-key add - || ( error "ERROR: Failed to get or load docker repo key." 1 )

request_admin "register docker repo"
echo "Registering docker repo on apt"
echo "deb [arch=amd64] https://download.docker.com/linux/${ID} ${VERSION_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/docker.list || ( error "ERROR: Failed to register docker repo." 1 )
sudo apt-get update -qq

request_admin "install docker"
echo "Installing docker..."
sudo apt-get -y -qq install docker-ce docker-ce-cli containerd.io || ( error "ERROR: Failed to install docker." 1 )

request_admin "add $USER to docker group"
sudo usermod -aG docker $USER || ( error "ERROR: Failed to add $USER to docker group." 1 )

request_admin "add socket folder to docker group"
echo "Creating shared directory for the docker socket..."
mkdir -pm o=,ug=rwx "$DOCKER_DIR" || ( error "ERROR: Failed to create the shared socket directory." 1 )
sudo chgrp docker "$DOCKER_DIR" || ( error "ERROR: Failed to add folder to docker group." 1 )|

request_admin "create docker config file"
echo "Creating docker config in $DOCKER_CFG..."
sudo mkdir -p $DOCKER_CFG || ( error "ERROR: Failed to create directory for docker config." 1 )
echo "{\n\t\"hosts\": [\"unix:///mnt/wsl/shared-docker/docker.sock\"]\n}" | sudo tee "$DOCKER_CFG/daemon.json"

request_admin "add docker to sudoers for passwordless invocation"
echo "%docker ALL=(ALL)  NOPASSWD: /usr/bin/dockerd" | sudo tee /etc/sudoers.d/01_docker || ( error "ERROR: Failed to edit sudoers file." 1 )

echo "#!/usr/bin/env sh
DOCKER_DISTRO=$DOCKER_DISTRO
DOCKER_DIR=$DOCKER_DIR
DOCKER_SOCK=$DOCKER_SOCK
if [ ! -S \"\$DOCKER_SOCK\" ]; then
  mkdir -pm o=,ug=rwx \"\$DOCKER_DIR\"
  chgrp docker \"\$DOCKER_DIR\"
  wsl.exe -d \$DOCKER_DISTRO sh -c \"nohup sudo -b dockerd < /dev/null > \$DOCKER_DIR/dockerd.log 2>&1\"
fi" > docker_init.sh || ( error "ERROR: Failed to generate init script." 1 )

if ! grep -q "DOCKER_HOST" "$shell_config"; then
  echo "Adding DOCKER_HOST variable to $shell_config..."
  echo "export DOCKER_HOST=\"unix://$DOCKER_SOCK\" # added by install-docker.sh script" >> $shell_config
  source $shell_config
fi

echo "Docker was installed successfully and a start script was generated. You should invoke it everytime before using docker. You may also add the invocation to your shell rc file, so it gets executed automatically when you login."

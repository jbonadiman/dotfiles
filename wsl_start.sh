sudo apt-get update && sudo apt-get upgrade

if [ ! -a ~/.inputrc ]; then echo '$include /etc/inputrc' > ~/.inputrc; fi

printf "setting up Vim"
git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim

printf "activating case insensitive tab-completion for the current user..."
echo 'set completion-ignore-case On' >> ~/.inputrc

printf "Dev Packages"
sudo apt-get install clang

printf "┌-------------------------------┐\n|      Docker installation      |\n└-------------------------------┘\n"

### uncomment to remove residue from other installations:
# sudo apt remove docker docker-engine docker.io containerd runc
echo "installing pre-requisites..."
sudo apt-get install --no-install-recommends apt-transport-https ca-certificates curl gnupg2

echo "setting some specific OS variables..."
source /etc/os-release

echo "making sure apt will trust the docker repository..."
curl -fsSL https://download.docker.com/linux/${ID}/gpg | sudo apt-key add -

echo "adding and updating repository information, so that apt uses it in the future..."
echo "deb [arch=amd64] https://download.docker.com/linux/${ID} ${VERSION_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update

echo "installing Docker Engine and client tools..."
sudo apt-get install docker-ce docker-ce-cli containerd.io -y

echo "adding $USER to docker group..."
sudo usermod -aG docker $USER

echo "hopefully, signing-in the new group..."
newgrp docker

echo "creating shared directory and setting permissions..."
DOCKER_DIR=/mnt/wsl/shared-docker
mkdir -pm o=,ug=rwx "$DOCKER_DIR"
chgrp docker "$DOCKER_DIR"

echo "creating docker configuration file..."
sudo mkdir -p /etc/docker
sudo printf "{\n\t\"hosts\": [\"unix:///mnt/wsl/shared-docker/docker.sock\"]\n}\n" > /etc/docker/daemon.json 

echo "adding auto-init to .bashrc..."
# TODO: find a way so the distro can be a variable
printf "DOCKER_DISTRO=\"Ubuntu-20.04\"\n" >> "~/.bashrc"
printf "DOCKER_DIR=/mnt/wsl/shared-docker\n" >> "~/.bashrc"
printf "DOCKER_SOCK=\"$DOCKER_DIR/docker.sock\"\n" >> "~/.bashrc"
printf "export DOCKER_HOST=\"unix://$DOCKER_SOCK\"\n" >> "~/.bashrc"
printf "if [ ! -S \"$DOCKER_SOCK\" ]; then\n" >> "~/.bashrc"
printf "    mkdir -pm o=,ug=rwx \"$DOCKER_DIR\"\n" >> "~/.bashrc"
printf "    chgrp docker \"$DOCKER_DIR\"\n" >> "~/.bashrc"
printf "    /mnt/c/Windows/System32/wsl.exe -d $DOCKER_DISTRO sh -c \"nohup sudo -b dockerd < /dev/null > $DOCKER_DIR/dockerd.log 2>&1\"\n" >> "~/.bashrc"
printf "fi\n" >> "~/.bashrc"



sudo apt-get install npm;
sudo npm install --global yarn;

yarn global add nvm;

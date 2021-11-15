#!/usr/bin/env zsh

echo "Installing essential packages..."
mkdir -p ~/tmp

if grep -q "^deb .*spvkgn/exa" /etc/apt/sources.list /etc/apt/sources.list.d/*; then
  echo "exa PPA repository already added, skipping..."
else
  echo "Adding exa PPA repository..."
  echo "Enter superuser (sudo) password to add the exa PPA repository to apt"
  sudo add-apt-repository ppa:spvkgn/exa -y
  apt-get update
fi

if exists bat; then
  echo "bat already installed, skipping..."
else
  echo "Installing bat..."
  wget -O ~/tmp/bat_0.18.3_amd64.deb https://github.com/sharkdp/bat/releases/download/v0.18.3/bat_0.18.3_amd64.deb
  echo "Enter superuser (sudo) password to install bat (v0.18.3)"
  sudo dpkg -i ~/tmp/bat_0.18.3_amd64.deb
fi

echo "Installing APT packages..."
echo "Enter superuser (sudo) password to install required apt packages"
xargs -a Essentials.pckg sudo apt install -y

if exists rustup; then
  echo "Rust already installed, skipping..."
else
  echo "Installing Rust..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
fi

if exists batman; then
  echo "bat extra modules already installed, skipping..."
else
  echo "Installing bat extra modules..."
  git clone "https://github.com/eth-p/bat-extras" ~/tmp/bat-extras
  echo "Enter superuser (sudo) password to install bat extra modules"
  sudo ~/tmp/bat-extras/build.sh --install
fi

if exists n; then
  echo "n already installed, skipping..."
else
  echo "Installing n..."
  curl -L "https://git.io/n-install" | bash -s -- -y
fi

echo "Setting up locale..."
sudo locale-gen pt_BR pt_BR.UTF-8
sudo update-locale

if [ ! -d ~/.vim/bundle/Vundle.vim ]; then
  echo "Installing Vundle..."
  git clone "https://github.com/VundleVim/Vundle.vim.git" ~/.vim/bundle/Vundle.vim
else
  echo "Vundle already installed, skipping..."
fi

echo "Enter superuser (sudo) password to delete the tmp folder created in this script"
sudo rm -rf ~/tmp

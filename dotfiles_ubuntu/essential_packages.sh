#!/usr/bin/env bash

echo "Installing essential packages and settings..."
mkdir -p ~/tmp

echo "Adding exa APT repository..."
sudo add-apt-repository ppa:spvkgn/exa -y
sudo apt-get update

if ! command -v bat &> /dev/null; then
  echo "Installing bat..."
  wget -O ~/tmp/bat_0.18.3_amd64.deb https://github.com/sharkdp/bat/releases/download/v0.18.3/bat_0.18.3_amd64.deb
  sudo dpkg -i ~/tmp/bat_0.18.3_amd64.deb
fi

echo "Installing APT packages..."
xargs -a Essentials.pckg sudo apt-get install -y

chsh -s /bin/zsh

if ! command -v rustup &> /dev/null; then
  echo "Installing Rust..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
fi

if ! command -v batman &> /dev/null; then
  echo "Installing bat extra modules..."
  git clone "https://github.com/eth-p/bat-extras" ~/tmp/bat-extras
  sudo ~/tmp/bat-extras/build.sh --install
fi

echo "Setting up locale..."
sudo locale-gen pt_BR pt_BR.UTF-8
sudo update-locale

if [ ! -d ~/.vim/bundle/Vundle.vim ]; then
  echo "Installing Vundle..."
  git clone "https://github.com/VundleVim/Vundle.vim.git" ~/.vim/bundle/Vundle.vim
fi

rm -rf ~/tmp

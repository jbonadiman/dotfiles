#!/usr/bin/env bash

echo "Installing essential packages and settings..."

sudo add-apt-repository ppa:spvkgn/exa -y
sudo apt-get update

xargs -a Essentials.pckg sudo apt-get install -y

# TODO: if $SHELL not zsh...
chsh -s /bin/zsh

# TODO: if rustup not installed...
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# TODO: if locale not set...
echo "Setting locale..."
sudo locale-gen pt_BR pt_BR.UTF-8
sudo update-locale

if [ ! -d ~/.vim/bundle/Vundle.vim ]; then
  echo "Installing Vundle..."
  git clone "https://github.com/VundleVim/Vundle.vim.git" ~/.vim/bundle/Vundle.vim
fi


#!/usr/bin/env bash

echo Installing essential packages...

sudo locale-gen pt_BR pt_BR.UTF-8
sudo update-locale

if [ ! -d ~/.vim/bundle/Vundle.vim ]; then git clone https://github.com/VundleVim/Vundle    .vim.git ~/.vim/bundle/Vundle.vim;fi

sudo add-apt-repository ppa:spvkgn/exa -y
sudo apt-get update

xargs -a Essentials.pckg  sudo apt-get install -y

curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

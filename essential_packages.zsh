#!/usr/bin/env zsh

if [ ! -d ~/.vim/bundle/Vundle.vim ]; then
  echo "Installing Vundle..."
  git clone "https://github.com/VundleVim/Vundle.vim.git" ~/.vim/bundle/Vundle.vim
else
  echo "Vundle already installed, skipping..."
fi

echo "Enter superuser (sudo) password to delete the tmp folder created in this script"
sudo rm -rf ~/tmp

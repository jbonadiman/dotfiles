#!/usr/bin/env sh

. ./zsh/utils

# links

ln -sf $(realpath ./zsh/.zshrc) ~/.zshrc
ln -sf $(realpath ./zsh/.zshenv) ~/.zshenv

# simple installations

echo "Requiring admin privilege to sync packages..."
sudo pacman -S --needed --noconfirm \
  zsh \
  yay \
  neovim \
  tree \
  python-pip \
  httpie \
  restic \
  clang \
  exa \
  make \
  openssh \
  go \
  tldr \
  bat

if exists pip; then
  sudo pip install --compile \
    trash-cli \
    neovim
fi

# scripts

chmod +x ./install_scripts/wsl/*
for script in ./install_scripts/wsl/*.*sh; do
  $script
  exit_code=$?
  if [ $exit_code -ne 0 ]; then
    echo "script $(echo $script) execution failed, status: $exit_code"
    exit $exit_code
  fi
done

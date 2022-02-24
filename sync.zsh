#!/usr/bin/env sh


source ./scripts/zsh_functions

# links

ln -sf $(realpath zshrc) ~/.zshrc
ln -sf $(realpath zshenv) ~/.zshenv
ln -sf $(realpath wezterm.lua) ~/.wezterm.lua

# simple installations

echo "Requiring admin privilege to sync packages..."
sudo pacman -S --needed --noconfirm \
  zsh \
  yay \
  neovim \
  python-pip \
  httpie \
  restic \
  clang \
  exa \
  make \
  openssh \
  go \
  bat

if exists pip; then
  sudo pip install --compile \
    trash-cli \
    neovim
fi

# scripts

chmod +x ./scripts/*
for script in ./scripts/*.*sh; do
  $script
  exit_code=$?
  if [ $exit_code -ne 0 ]; then
    echo "script $(echo $script) execution failed, status: $exit_code"
    exit $exit_code
  fi
done

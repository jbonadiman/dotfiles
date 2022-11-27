#!/usr/bin/env sh

scripts_path=$(realpath $(dirname $(readlink -f $0)))
. $scripts_path/../zsh/utils

if exists batman
then
  echo bat-extras is already installed, skipping...
  exit 0
fi

echo this script installs shfmt to make sure bat-extras will be minified on installation

if ! exists go
then
  echo requiring admin privileges to install go...
  sudo pacman -S go
fi

if ! exists shfmt
then
  go install mvdan.cc/sh/v3/cmd/shfmt@latest
fi

echo downloading bat-extras sources...
git clone https://github.com/eth-p/bat-extras.git /tmp/bat-extras

echo installing bat-extras...
cd /tmp/bat-extras
sudo ./build.sh --minify=all --install
sudo rm -r /tmp/bat-extras

echo bat-extras was installed successfully!

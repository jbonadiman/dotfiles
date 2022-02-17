#!/usr/bin/env sh

scripts_path=$(realpath $(dirname $(readlink -f $0)))

source $scripts_path/zsh_functions

if exists node; then
  echo "node is already installed, skipping..."
else
  if ! exists n; then
    "./install-n.sh"
  fi

  echo "Installing node..."
  n lts
fi

echo "Done!"

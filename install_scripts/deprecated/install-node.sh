#!/usr/bin/env sh

scripts_path=$(realpath $(dirname $(readlink -f $0)))
. $scripts_path/../zsh/utils

if exists node
then
  echo node is already installed, skipping...
else
  if ! exists n
  then
    "$scripts_path/install-n.sh"
  fi

  echo installing node...
  n lts
fi

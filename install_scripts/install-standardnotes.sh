#!/usr/bin/env sh

scripts_path=$(realpath $(dirname $(readlink -f $0)))
. $scripts_path/../zsh/utils

if exists standard-notes
then
  echo standard notes already installed, skipping...
else
  git clone https://aur.archlinux.org/standardnotes-bin.git /tmp/standardnotes
  cd /tmp/standardnotes

  makepkg -si --noconfirm
  echo done!
fi

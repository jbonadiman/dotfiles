#!/usr/bin/env sh

if exists standardnotes-desktop
then
  echo standard notes already installed, skipping...
else
  git clone https://aur.archlinux.org/standardnotes-desktop.git /tmp/standardnotes
  cd /tmp/standardnotes

  makepkg -si --noconfirm
  echo done!
fi

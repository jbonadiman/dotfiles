#!/usr/bin/env zsh

echo "Starting ZSH setup"

if exists zsh; then
  echo "zsh found, skipping installation..."
else
  echo "Enter superuser (sudo) password to install zsh"
  sudo apt install zsh
fi

if [ "$SHELL" = '/usr/bin/zsh' ]; then
  echo '$SHELL is already zsh, skipping...'
else
  echo "Enter superuser (sudo) password to change login shell"
  sudo chsh -s $(which zsh)
fi

if readlink -f /usr/bin/sh | grep -q zsh; then
  echo '/usr/bin/sh already linked to /usr/bin/zsh'
else
  echo "Enter superuser (sudo) password to symlink sh to zsh"
  sudo ln -sfv /usr/bin/zsh /usr/bin/sh
fi

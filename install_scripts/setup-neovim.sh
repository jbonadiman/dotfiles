#!/usr/bin/env sh

scripts_path=$(realpath $(dirname $(readlink -f $0)))

source $scripts_path/zsh_functions

# TODO: install LunarVim

vimrc_folder=$(realpath $(dirname $(readlink -f $0))/..)/vimrc
nvim_folder=${NVIM_HOME:-$HOME/.config/nvim}

if exists nvim; then
  echo neovim already installed, skipping...
else
  echo installing neovim...
  sudo pacman -Syu neovim
fi

if [ -L $nvim_folder/init.vim ] && [ $(readlink -f $nvim_folder/init.vim) == $vimrc_folder ]; then
  echo neovim config already linked, skipping...
else
  echo linking init.vim...
  mkdir -p $nvim_folder
  ln -sf $vimrc_folder $nvim_folder/init.vim
fi

if [ -f $nvim_folder/autoload/plug.vim ]; then
  echo vim.plug already installed, skipping...
else
  echo installing vim-plug...
  curl -fLo $nvim_folder/autoload/plug.vim --create-dirs \
    "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim"  > /dev/null
fi

echo installing neovim plugins...
nvim --headless +PlugInstall +qa

if exists yarn; then
  echo yarn already installed, skipping...
else
  echo installing yarn...
  sudo pacman -S yarn
fi

echo installing coc.vim dependencies...
cd ~/.local/share/nvim/plugged/coc.nvim
yarn install > /dev/null

echo Done!

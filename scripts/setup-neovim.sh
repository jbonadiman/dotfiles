#!/usr/bin/env sh

function exists() {
  command -v $1 >/dev/null 2>&1
}

vimrc_folder=$(realpath $(dirname $(readlink -f $0))/..)/vimrc
nvim_folder=${NVIM_HOME:-$HOME/.config/nvim}

if exists nvim; then
  echo "neovim already installed, skipping..."
else
  echo "Installing neovim..."
  sudo pacman -Syu neovim
fi

if [ -L $nvim_folder/init.vim ] && [ $(readlink -f $nvim_folder/init.vim) == $vimrc_folder ]; then
  echo "neovim config already linked, skipping..."
else
  echo "Linking init.vim..."
  mkdir -p $nvim_folder
  ln -sf $vimrc_folder $nvim_folder/init.vim
fi

if [ -f $nvim_folder/autoload/plug.vim ]; then
  echo "vim.plug already installed, skipping..."
else
  echo "Installing vim-plug..."
  curl -fLo $nvim_folder/autoload/plug.vim --create-dirs \
    "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim"  > /dev/null
fi

echo "Installing neovim plugins..."
nvim --headless +PlugInstall +qa

if exists yarn; then
  echo "yarn already installed, skipping..."
else
  echo "Installing yarn..."
  sudo pacman -S yarn
fi

echo "Installing coc.vim dependencies..."
cd .local/share/nvim/plugged/coc.nvim
yarn install > /dev/null

echo "Done!"

#!/usr/bin/env sh

# Install neovim

# Link init.vim

# Install vim-plug

# Install plugins

# Install node

# Install yarn
sudo pacman -Syu yarn

# Install coc.vim dependencies
cd .local/share/nvim/plugged/coc.nvim
yarn install

#!/usr/bin/env sh

plugins_folder=$HOME/.zsh
repo_base=https://github.com/zsh-users

if [ -d $plugins_folder ]; then
  echo plugins\' folder $(basename $plugins_folder) already exists, skipping creation...
else
  echo creating folder $(basename $plugins_folder)...
  mkdir -p $plugins_folder
fi

plugins_list="zsh-autosuggestions"
plugins_list="${plugins_list} zsh-syntax-highlighting"

for plugin in ${plugins_list}; do 
  if [ -d $plugins_folder/$plugin ]; then
    echo plugin $plugin already installed, skipping...
    continue
  fi

  echo installing $plugin...
  git clone $repo_base/$plugin $plugins_folder/$plugin
done


#!/usr/bin/env sh

plugins_folder=$HOME/.zsh
repo_base=https://github.com/zsh-users

if [ -d $plugins_folder ]; then
  echo Plugins\' folder "'$(basename $plugins_folder)'" already exists. Skipping creation...
else
  echo Creating folder "'$(basename $plugins_folder)'"...
  mkdir -p $plugins_folder
fi

plugins_list=(
  "zsh-autosuggestions"
  "zsh-syntax-highlighting"
)

for plugin in ${plugins_list[@]}; do 
  if [ -d $plugins_folder/$plugin ]; then
    echo Plugin "'$plugin'" already installed. Skipping...
    continue
  fi

  echo Installing "'$plugin'"...
  git clone $repo_base/$plugin $plugins_folder/$plugin
done


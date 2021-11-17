#!/usr/bin/env zsh
script_path="$(dirname ${(%):-%x})"
echo $script_path
cd $script_path

read -q "REPLY?This is the question I want to ask?"

# functions


# Create folders
folders=(
    "~/sources"
    "~/.local/bin"
)

for dir in ${(u)folders[@]}; do
    absolute=dirname $dir
    echo $absolute
    if [ -d $absolute ]; then
        echo "Directory '$absolute' already exists, skipping creation..."
    else
        echo "Creating directory '$absolute'..."
        mkdir -p $absolute
    fi
done


# Create links

links=(
    "~/.vimrc:./vimrc"
    "~/.zshrc:./zshrc"
)

for link in ${(u)links[@]}; do
    IFS=: read dst src <<< $link
    abs_dst=dirname $dst
    abs_src=dirname $src
    if [ ! readlink -e $abs_src ]; then
        echo "Source location '$abs_src' does not exist, skipping..."
        continue
    fi
    echo "Linking '$abs_dst' to '$abs_src'..."
    ln -sf $abs_dst $abs_src
done

# Execute procedures/scripts

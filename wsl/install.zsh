#!/usr/bin/env zsh
# functions


# Create folders
folders=(
    "~/sources"
    "~/.local/bin"
)

for dir in ${(u)folders[@]}; do
    echo $dir
    if [ -d $dir ]; then
        echo "Directory '$dir' already exists, skipping creation..."
    else
	echo "Creating directory '$dir'..."
        mkdir -p $dir
    fi 
done


# Create links

links=(
    "~/.vimrc:vimrc"
    "~/.zshrc:zshrc"
)

for link in ${(u)links[@]}; do
    IFS=: read dst src <<< $link
    if [ ! readlink -e $src ]; then
        echo "Source location '$src' does not exist, skipping..."
	continue
    fi 
    echo "Linking '$dst' to '$src'..."
    ln -sf $dst $src 
done

# Execute procedures/scripts

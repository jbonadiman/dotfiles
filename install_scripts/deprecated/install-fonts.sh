#!/usr/bin/env sh



fonts_folder=/tmp/fonts


mkdir -p $fonts_folder/fira-code

curl https://github.com/tonsky/FiraCode/releases/download/6.2/Fira_Code_v6.2.zip -o /tmp/fonts/fira-code/fira-code.zip
curl https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/NerdFontsSymbolsOnly/complete/Symbols-1000-em%20Nerd%20Font%20Complete.ttf -o "/tmp/fonts/Symbols-1000-em Nerd Font Complete.ttf"
curl https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/NerdFontsSymbolsOnly/complete/Symbols-1000-em%20Nerd%20Font%20Complete%20Mono.ttf -o "/tmp/fonts/Symbols-1000-em Nerd Font Complete Mono.ttf"

previous_wd=$(pwd)

cd $fonts_folder/fira-code
unzip fira-code.zip
rm fira-code.zip
cd $previous_wd

echo Requiring admin privileges to install Fira Code and Nerd Font Symbols
sudo mv $fonts_folder/* /usr/share/fonts

echo done!

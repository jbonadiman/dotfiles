#!/usr/bin/env sh

###
printf "setting up mirrors list..."

mirrorlist='/etc/pacman.d/mirrorlist'
mirrorlist_arch='https://archlinux.org/mirrors/status'

printf "getting the best mirror rated on %s...\n" "$mirrorlist_arch"
best_mirror=$(curl -s "$mirrorlist_arch/json/" | jq -r '.urls | map(select(.active and .score != null)) | min_by(.score) | .url')

printf "creating mirrorlist backup..."
sudo cp "$mirrorlist" "$mirrorlist.bak"
new_mirrorlist_content=$(printf '# Best mirror\n%s$repo/os/$arch\n\n' "$best_mirror"; cat "$mirrorlist")

printf "writing result to %s...\n" "$mirrorlist"
printf "%s" "$new_mirrorlist_content" | sudo tee $mirrorlist 1>/dev/null

###
printf "setting up arch keyring..."

sudo pacman-key --init
sudo pacman-key --populate archlinux
sudo pacman -Sy --noconfirm archlinux-keyring

printf "updating pacman..."
sudo pacman -Syu --noconfirm base
sudo pacman -Fy --noconfirm

###
printf "creating user %s..." "$1"
sudo useradd -m -G wheel $1
sudo passwd $1

printf "adjusting wheel group permissions..."
sudoers='\etc\sudoers'

printf "creating sudoers backup..."
sudo cp "$sudoers" "$sudoers.bak"

sudo cat "$sudoers" | sed -E 's/^# (%wheel ALL=\(ALL:ALL\) ALL)$/\1/' | sudo tee "$sudoers" 1>/dev/null

printf "done! User '%s' created successfully!" "$1"
###

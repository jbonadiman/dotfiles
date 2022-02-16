echo "Getting genie sources..."
git clone https://aur.archlinux.org/genie-systemd-git.git /tmp/genie-systemd

echo "Installing genie"
(cd /tmp/genie-systemd && makepkg -si)

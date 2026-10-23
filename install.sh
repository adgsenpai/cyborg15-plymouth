#!/bin/sh
# Install the Cyborg 15 Plymouth theme and make it the default boot splash.
set -e
cd "$(dirname "$0")"
T=/usr/share/plymouth/themes/cyborg
sudo rm -rf "$T"
sudo cp -r cyborg "$T"
sudo update-alternatives --install /usr/share/plymouth/themes/default.plymouth default.plymouth "$T/cyborg.plymouth" 200
sudo update-alternatives --set default.plymouth "$T/cyborg.plymouth"
sudo update-initramfs -u

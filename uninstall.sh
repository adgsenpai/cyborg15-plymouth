#!/bin/sh
# Remove the Cyborg 15 theme; Plymouth falls back to the next theme (bgrt on Ubuntu).
set -e
T=/usr/share/plymouth/themes/cyborg
sudo update-alternatives --remove default.plymouth "$T/cyborg.plymouth" || true
sudo update-alternatives --auto default.plymouth
sudo rm -rf "$T"
sudo update-initramfs -u

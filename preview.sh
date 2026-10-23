#!/bin/sh
# Preview the installed theme in a window (needs plymouth-x11) without rebooting.
# Shows the boot screen, then a fake LUKS prompt (type anything, Enter to finish).
sudo env DISPLAY="${DISPLAY:-:0}" XAUTHORITY="$XAUTHORITY" /usr/sbin/plymouthd --no-daemon --no-boot-log &
sleep 2
sudo plymouth show-splash
for p in 10 30 50 70 90; do sudo plymouth system-update --progress=$p; sleep 1; done
sudo plymouth display-message --text="Preview: type anything and press Enter"
sudo plymouth ask-for-password --prompt="Please unlock disk (preview)" --command=/bin/true
sudo plymouth quit

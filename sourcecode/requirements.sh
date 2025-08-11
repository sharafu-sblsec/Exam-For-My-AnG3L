#!/bin/bash
set -euxo pipefail

ORIG_USER="$SUDO_USER"
if [ -z "$ORIG_USER" ]; then
    ORIG_USER="$USER"
fi

if [ "$EUID" -ne 0 ]; then
    echo "You are not root... Requesting password to switch to root ..."
    sudo -v || { echo "Password incorrect or sudo not allowed.... Exiting."; exit 1; }
    echo "Switching to root..."
    sudo bash -c '
        set -euxo pipefail
        apt update -y
        apt install -y python3-pip python3-flask redis-server python3-redis
    '
else
    echo "You are already root. Installing packages..."
    apt update -y
    apt install -y python3-pip python3-flask redis-server python3-redis
fi

if [ "$EUID" -eq 0 ] && [ "$ORIG_USER" != "root" ]; then
    echo "Switching back to normal user: $ORIG_USER"
    su - "$ORIG_USER"
else
    echo "Installation complete.Switching To User Failed."
fi

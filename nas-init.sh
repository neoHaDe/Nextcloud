#!/bin/sh

if [ -d "/mnt/nas" ]; then
    chown -R 33:33 /mnt/nas
    chmod -R 770 /mnt/nas
fi


exec /entrypoint.sh "$@"

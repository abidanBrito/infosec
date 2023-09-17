#!/bin/bash

# Only run this script inside Docker as root user!
# It will change file permissions and ownership
id -u ssd &> /dev/null
if [[ "$?" -ne "0" ]]; then
  echo "You should run this script only inside Docker"
  exit 1
fi

if [[ "${PWD#/mnt/host}" != "${PWD}" ]]; then
  echo "You should run this script outside /mnt/host"
  exit 1
fi

echo "Preparing test system permissions"
chmod 500 exploit
chown -R exploit:exploit .
chown hacklet:hacklet main.elf
chmod 2575 main.elf
chown hacklet:hacklet flag.txt
chmod 440 flag.txt
echo "Running exploit"
sudo -u exploit ./exploit

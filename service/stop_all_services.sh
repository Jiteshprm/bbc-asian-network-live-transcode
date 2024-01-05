#/bin/bash
set -x
#Must be run as sudo
if [ $EUID -ne 0 ]
  then echo "Please run with sudo!"
  exit
fi


systemctl daemon-reload
systemctl stop bbc-anlt.service
systemctl disable bbc-anlt.service



#/bin/bash
set -x
#Must be run as sudo
if [ $EUID -ne 0 ]
  then echo "Please run with sudo!"
  exit
fi


cp bbc-anlt.service /etc/systemd/system
systemctl daemon-reload
systemctl enable bbc-anlt.service
systemctl start bbc-anlt.service


#!/bin/bash

echo "stop service"
sudo service pipymo stop

echo "disabling service"
sudo systemctl disable pipymo

echo "remove link"
sudo rm /usr/local/bin/pipymo

echo "remove service file"
sudo rm /etc/systemd/system/pipymo.service

echo "Please delete manually the pipymo folder and the configuration on ~/.pipymo/*"
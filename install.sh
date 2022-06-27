#!/bin/bash


SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

sudo rm -f /usr/local/bin/pipymo

sudo chmod 744 $SCRIPT_DIR/__main__.py
sudo chmod +x  $SCRIPT_DIR/__main__.py

sudo ln -s $SCRIPT_DIR/__main__.py /usr/local/bin/pipymo

sudo cp $SCRIPT_DIR/pipymo.service /etc/systemd/system/

pip install -r $SCRIPT_DIR/requirements.txt


echo "if you want enable the http service with\n sudo systemctl enable pipymo && sudo systemctl start pipymo"
echo "Done! use it with -> pipymo echo"
#!/bin/bash

CONFIG_FOLDER="/home/$USER/.pipymo"

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# set the current user on service file 
sed -i -e "s/REPLACE_THIS_USERNAME/$USER/g" $SCRIPT_DIR/pipymo.service

if [ -d "$CONFIG_FOLDER" ]; then
    echo ".pipymo folder exists, skipping copy of defaults..." 
else
    mkdir "$CONFIG_FOLDER"
    cp "$SCRIPT_DIR/config/*" "$CONFIG_FOLDER/"
fi

if [ -f "/usr/local/bin/pipymo" ]; then
    echo ".pipymo was previously installed removing /usr/local/bin/pipymo" 
    echo "if you are running it as a script please restart the flask server using:"
    echo "-> sudo systemctl restart pipymo"
    sudo rm -f /usr/local/bin/pipymo
fi

sudo chmod 744 "$SCRIPT_DIR/__main__.py"
sudo chmod +x  "$SCRIPT_DIR/__main__.py"

sudo ln -s "$SCRIPT_DIR/__main__.py" "/usr/local/bin/pipymo"

sudo cp "$SCRIPT_DIR/pipymo.service" "/etc/systemd/system/"

pip install -r "$SCRIPT_DIR/requirements.txt"


echo "if you want enable the http service with:"
echo "sudo systemctl enable pipymo && sudo systemctl start pipymo"
echo "Done! Check it with -> pipymo echo"

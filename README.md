# PiPyMon

Raspberry pi* lightweight monitoring tool in python

pipymo is a cli monitoring tool writen in python it uses flask to serve as a prometheus exporter and a json api if you want to. 

pipymo wraps a bunch of shell commands and parses it to monitor:

> you can disable or costumize some options in your config file -> /home/YOUR_USERNAME/.pipymo/config.yaml

- CPU usage
- CPU temperature
- RAM and swap usage
- running processes / total processes
- System load average (1, 5, 15) min 
- Disk usage
- measure network traffic 

Besides the monitoring part i added some other small but usefull ( at least for me ) commands like getting the public ip of your network and ping some defined hosts for connectivity check.

![Raspberry pi monitoring cli usage](imgs/pipymo_echo_scs.jpg "'pipymo echo' example output")

# Usage

pipymo echo -> to output the current status to console
pipymo serve -> to start http server will serve /json and /metrics endpoints with the same information that you get on "echo" command

pipymo ping -> to ping your hosts defined in your config folder -> /home/YOUR_USERNAME/.pipymo/ping_hosts.txt
pipymo myip -> to get your public IP. This makes a request to https://api.ipify.org presenting you with the result


## How to use it 

```shell
git clone git@github.com:dirop1/pipymo.git && cd pipymo 
pip install -r requirements.txt
python3 . echo
```

## Instalation and auto start up

```shell
chmod +x install.sh
sudo ./install.sh
```
the pipymo service will be installed by now
you can now run commands like:

```shell
pipymo myip
```

if you want enable the http server at start up just enable the service service with:

```shell
sudo systemctl enable pipymo && sudo systemctl start pipymo
```

# Costumization

In the config folder of this repo there is 2 files that you should place in ~/.pipymo/ (if you used the install script they will be there by now) 

Just edit the files to suite your needs.

- The config.yaml is a configuration file that specify to pipymo what to monitor and the http port to use when using the http server (read the comments in the configuration file to get more info)
- The ping_hosts.txt is just a line-separated list of hosts that will be ping'd when you run the "pipymo ping" command

> * it should work too in debian based distros
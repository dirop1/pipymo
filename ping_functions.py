#!/bin/bash

import os
import platform    # For getting the operating system name
import subprocess  # For executing a shell command


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print("******** PingChecker **********")

def progressBar(name, current, total, barLength = 30):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))

    print(bcolors.OKCYAN +'Progress: [%s%s] %d %%   %d - Host: %s' % (arrow, spaces, percent,current,name), end='\r')


def ping(count,host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """
    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['timeout','1.5','ping',  param, '1', host]

    return subprocess.call(command, 
    stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT) == 0

# dir_path = os.path.dirname(os.path.realpath(__file__))

# Using readlines()
cur_user = os.environ.get('USER')
hosts_ping_config_file_path = '/home/'+ cur_user +'/.pipymo/ping_hosts.txt'
if not os.path.exists(hosts_ping_config_file_path):
    print("You need to create a file with the hosts you want to ping in ~/.pipymo/ping_hosts.txt to use this function " )
else:
    ping_hosts_file = open(hosts_ping_config_file_path, 'r')
    Lines = ping_hosts_file.readlines()
    total_lines = len(Lines)

    count = 0
    results = []
    for line in Lines:
        count += 1
        host = line.rstrip()
        # print(host, "-", ip)
        online = ping(count, host)
        # print("{} - host: {} ip: {} : {}".format(count, host, ip, online ))
        online_emoji = [bcolors.OKGREEN+'✅', bcolors.FAIL+'❌'][not online]
        results.append([count, host, online_emoji ])
        progressBar(host,count, total_lines)

    print(bcolors.HEADER +"----------------------------------- Done ---------------------------------", end='\r')
    print(bcolors.ENDC)

    for result in results:
        # print("{} - host: {} ip: {} : {}".format(result))
        print(f"{result[2]} - {result[0]} - {result[1]}" + bcolors.ENDC)
    ping_hosts_file.close()
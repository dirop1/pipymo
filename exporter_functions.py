import yaml
import subprocess
import os
import time

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

config = None

#only available for raspberry pi ATM
cpu_temp_available = True

mean_metrics = {"rxtx": []}
cached_result_cores = 0

def getCliOutput(cmd):
    output = subprocess.check_output(cmd, shell=True).decode("utf-8") 
    return output.split("\n")

    
def loadCpu():
    global cpu_temp_available
    try:
        getCliOutput("cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null")
    except subprocess.CalledProcessError:
        print(f"{bcolors.FAIL}cpu temp is not available{bcolors.ENDC}")
        cpu_temp_available = False

def checkConfigExist(key):
    return key in config

def getNetworkRXTX(device_name):
    return getCliOutput(f"cat /sys/class/net/{device_name}/statistics/rx_bytes 2>/dev/null && cat /sys/class/net/{device_name}/statistics/tx_bytes 2>/dev/null")

available_net_devices = []
#cat /sys/class/net/eth0/statistics/rx_bytes && cat /sys/class/net/eth0/statistics/tx_bytes
def loadNetworks():
    if checkConfigExist('rxtx'):
        for netd in config['rxtx']:
            try:
                getNetworkRXTX(netd)
                available_net_devices.append(netd)
            except subprocess.CalledProcessError:
                print(f"{bcolors.FAIL}Network device {netd} is not available{bcolors.ENDC}")

def loadCmds():
    try:
        if checkConfigExist("cmds"):
            if config["cmds"]["start"]:
                print("Running start command...")
                print(config["cmds"]["start"])
                getCliOutput(config["cmds"]["start"])
    except:
        print("error on start command")

def exiting():
    try:
        if checkConfigExist("cmds"):
            print("Running exit command...")
            print(config["cmds"]["stop"])
            getCliOutput(config["cmds"]["stop"])
    except:
        print("error on exit command")

def startUpExporter():
    loadCpu()
    loadNetworks()

    
#read config\
cur_user = os.environ.get('USER')
dir_path = os.path.dirname(os.path.realpath(__file__))
default_config_file_path = dir_path + '/config/config.yaml'
user_config_file_path = '/home/'+ cur_user +'/.pipymo/config.yaml'

config_file_path = ""
if not os.path.exists(user_config_file_path):
    print(f"{bcolors.FAIL} Using the default config file create one in ~/.pipymo/config.yaml to use your own...{bcolors.ENDC}")
    config_file_path = default_config_file_path
else:
    config_file_path = user_config_file_path



with open( config_file_path ) as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)
    print("Loaded config file " + config_file_path)


def loadDisksInfo():
    df_output = getCliOutput("df -l -BM --output=target,used,avail,pcent | awk '{if (NR!=1) {print $1,$2,$3,$4}}'")
    result = []
    for o in df_output:
        splited_df = o.split(" ")
        for index, disk in enumerate(config['disks']):
            if disk == splited_df[0]:
                result.append({
                    'mountpoint': splited_df[0],
                    'used': tryInt(splited_df[1].replace("M","")),
                    'avail': tryInt(splited_df[2].replace("M","")),
                    'pcent': tryInt(splited_df[3].replace("%","")),
                })
    return result

def tryInt(maybe_number):
    try:
        return int(maybe_number)
    except:
        return maybe_number


def updateInfo():
    global mean_metrics,cached_result_cores
    last_checked = 0
    if mean_metrics.get("lc"):
        last_checked = mean_metrics.get("lc")

    result = {}
    if not cached_result_cores:
        cached_result_cores = tryInt(getCliOutput("grep -c ^processor /proc/cpuinfo")[0])
    
    result['cores'] = cached_result_cores

    	
    if checkConfigExist("cpu"):
        if cpu_temp_available:
            result['cputemp'] = tryInt(tryInt(getCliOutput("cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null")[0])/ 1000)
        else:
            result['cputemp'] = -1
        # result['loadavg'] = getCliOutput()
    if checkConfigExist("loadavg"):
        loadavg = getCliOutput("cat /proc/loadavg")[0].split(" ")
        result['load1'] = float(loadavg[0])
        result['load5'] = float(loadavg[1])
        result['load15'] =float(loadavg[2])
        result['load_pcent'] = result['load1'] / result['cores'] * 100
        proc = loadavg[3].split("/")
        result['running_processes'] = tryInt(proc[0])
        result['total_processes'] = tryInt(proc[1])
    if checkConfigExist("ram"):
        free_output = getCliOutput("free --mega | awk '{if (NR!=1) {print $2,$3,$4}}'")
        free_mem = free_output[0].split(" ")
        free_swap = free_output[1].split(" ")
        result['memory_max'] = tryInt(free_mem[0])
        result['memory_used'] = tryInt(free_mem[1])
        result['swap_max'] = tryInt(free_swap[0])
        result['swap_used'] = tryInt(free_swap[1])
    if checkConfigExist("rxtx"):
        result["rxtx"] = []
        for index, netd in enumerate(available_net_devices):

            dev_stats = getNetworkRXTX(netd)
            new_stats_device = {
                "device" : netd,
                "rx" : tryInt(tryInt(dev_stats[0]) / 1024), # in kilobytes
                "tx" : tryInt(tryInt(dev_stats[1]) / 1024) # in kilobytes
            }
            
            # if we have a last read we can compute the diference beteen the teime range
            if last_checked:
                result["rxtx_s"] = []
                time_dif_seconds = time.time() - last_checked
                new_0 = (new_stats_device["rx"] - mean_metrics[netd]["rx"]) / time_dif_seconds
                new_1 = (new_stats_device["tx"] - mean_metrics[netd]["tx"]) / time_dif_seconds
                result["rxtx_s"].append({
                    "device" : netd,
                    "rx_s" : tryInt(new_0), # in kilobytes
                    "tx_s" : tryInt(new_1) # in kilobytes
                })
                
            mean_metrics[netd] = new_stats_device
            result["rxtx"].append(new_stats_device)

    if checkConfigExist("disks"):
        result['disks'] = loadDisksInfo()

    mean_metrics["lc"] = time.time()

    return result




def prometheusExporter(info):
    result = "#HELP pipymo\n"
    for key in info:
        if key != "disks" and key != "rxtx" and key != "rxtx_s":
            scientific_notation = "{:.2e}".format(info[key])
            result = result + f"{key} {scientific_notation}"+"\n" 
    if "disks" in info:
        for disk in info['disks']:
            for key in disk:
                if key != "mountpoint":
                    scientific_notation = "{:.2e}".format(disk[key])
                    result = result + "disk_" + key+ "{mountpoint=\""+ disk["mountpoint"] + "\"} "+scientific_notation+"\n" 
    for net_rxrtx in ["rxtx", "rxtx_s"]:
        if net_rxrtx in info:
            for netd in info[net_rxrtx]:
                for key in netd:
                    if key != "device":
                        scientific_notation = "{:.2e}".format(netd[key])
                        result = result + "net_device_" + key+ "{device=\""+ netd["device"] + "\"} "+scientific_notation+"\n" 
    return result

def echoCliOutput(info, hostname):
    print(f"*******************  {bcolors.OKBLUE}pipymo - {hostname}{bcolors.ENDC}  *******************") 
    for key in info:
        if key != "disks" and key != "rxtx":
            print(f"{bcolors.OKCYAN}{key}: {bcolors.WARNING}{info[key]}{bcolors.ENDC}") 
    if "disks" in info:
        print(f"{bcolors.UNDERLINE}disks:{bcolors.ENDC}")
        if len(info['disks']) == 0:
            print(f"{bcolors.FAIL}  Nothing found{bcolors.ENDC}")
        for disk in info['disks']:
            print(f"{bcolors.OKGREEN}  montpoint: " + disk["mountpoint"]+f"{bcolors.ENDC}")
            for key in disk:
                if key != "mountpoint":                    
                    print(f"{bcolors.OKCYAN}    " + key+ f": {bcolors.WARNING}"+ str(disk[key]) +f"{bcolors.ENDC}")
    if "rxtx" in info:
        print(f"{bcolors.UNDERLINE}net devices:{bcolors.ENDC}")
        if len(info['rxtx']) == 0:
            print(f"{bcolors.FAIL}  Nothing found{bcolors.ENDC}")
        for netd in info['rxtx']:
            print(f"{bcolors.OKCYAN}  device: " + netd["device"] +f"{bcolors.ENDC}")
            for key in netd:
                if key != "device":
                    print("    " + key + f": {bcolors.WARNING}"+ str(netd[key]) +f"{bcolors.ENDC}") 

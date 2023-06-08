#!/usr/bin/python3 

import sys
from flask import Flask, Response, request
import json 
from exporter_functions import *
import socket
import sys
import subprocess
import logging

# setting the log level to error to preserve the sd card writes
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


authorization_header = None
hostname = socket.gethostname()



def echoHelp():
    print(hostname)
    print("Need at least 1 argument:")
    print("  'echo' to output the current status to console")
    print("  'serve' to start http server")
    print("  'ping' to ping your hosts defined in the config folder")
    print("  'myip' to get your public IP. This makes a request to https://api.ipify.org")
    print("  'help' to see this message again")
    print("Have a nice day.")

if (len(sys.argv) <= 1):
    echoHelp()
    exit(1)

if (len(sys.argv) > 1):
    if sys.argv[1] == "help":
        echoHelp()
        exit(0) 
    elif sys.argv[1] == "ping":
        import ping_functions
        exit(0) 
    if sys.argv[1] == "myip":
        print(f"*******************  {bcolors.OKBLUE}pipymo - Public Ip {bcolors.ENDC}  *******************") 
        print(getCliOutput("curl -s https://api.ipify.org"))
        exit(0)
    elif sys.argv[1] == "echo" or sys.argv[1] == "serve":
        from exporter_functions import *
        startUpExporter()
        if checkConfigExist("http_config"):
            try:
                if config["http_config"]["auth_header"]:
                    authorization_header = config["http_config"]["auth_header"]
                    print(config["http_config"]["auth_header"])
            except:
                print("Error parsing auth_header")
                pass
        if sys.argv[1] == "echo":
            echoCliOutput(updateInfo(), hostname)
            exit(0)
        if sys.argv[1] == "serve":
            if not checkConfigExist("http_config"):
                print("Need the http_config in config.yaml")
                exit(2)
            pass
    else:
        echoHelp()
        exit(1)


def checkHeaders():
    global authorization_header
    print(authorization_header)
    if authorization_header != None:
        return config["http_config"]["auth_header"] == request.headers.get('Authorization')
    return True

app = Flask(__name__)
@app.route(config["http_config"]["paths"]["prometheus"])
def metrics():    
    if checkHeaders():    
        return Response(prometheusExporter(updateInfo()),mimetype='text/plain')
    return Response("Unauthorized", status=401, mimetype='text/plain')

@app.route(config["http_config"]["paths"]["json"])
def rjson(): 
    if checkHeaders():       
        return Response(json.dumps(updateInfo()), mimetype='application/json')
    return Response("Unauthorized", status=401, mimetype='text/plain')

#function to run comands on shell that are declared on config file
@app.route("/exec-cmd/<cmd>")
def execCmds(cmd): 
    if checkHeaders():   
        http_conf = config.get("http_config") 
        if http_conf.get("cmds") and http_conf.get("cmds").get(cmd):    
            try:                
                result = subprocess.run(http_conf.get("cmds").get(cmd).split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return Response(json.dumps({
                                'output': result.stdout.decode('utf-8'),
                                "error": None
                            }), status=200, mimetype='application/json')
            except:
                return Response(json.dumps({
                                'output': None,
                                "error": "That was an error"
                            }), status=500, mimetype='application/json')
        else:
            return Response("Not found", status=404, mimetype='text/plain')
    else:
        return Response("Unauthorized", status=401, mimetype='text/plain')

if __name__ == '__main__' and checkConfigExist('http_config'):
    loadCmds()
    server = app.run(host='0.0.0.0', port=config['http_config']['port'], debug=False)
    exiting()
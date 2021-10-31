from flask import Flask, json, jsonify, request
import argparse

import requests


flask_app = Flask(__name__)
hostname = '0.0.0.0'
port = 8080

# Some default game params
N_DEFAULT = 5
K_DEFAULT = 9
P_DEFAULT = 3

# Keeping tabs on tunneler and detector
tunneler = {}
detector = {}

@flask_app.route('/registration', methods=['GET'])
def register():
    role = request.args.get("role")
    name = request.args.get("name")
    
    if(not name or not role):
        return "Please send both name and role (Detector/Tunneler)", 412
    elif(not (role == "Tunneler" or role == "Detector")):
        return "Invalid role: please send either Detector or Tunneler", 412
    elif(role == "Tunneler" and "reg" in tunneler):
        return "Tunneler role already taken", 412
    elif(role == "Detector" and "reg" in detector):
        return "Detector role already taken", 412

    print("Registering name: ", request.args.get("name"), " and role: ", request.args.get("role"))
    print_wait()

    if(role == "Tunneler"):     tunneler["reg"] = name
    elif(role == "Detector"):   detector["reg"] = name

    return jsonify({
        "n": args.n,
        "k": args.k,
        "p": args.p
    })

def print_wait():
    if(not "reg" in tunneler):
        print("Waiting for tunneler to register")
    elif(not "reg" in detector):
        print("Waiting for detector to register")
    
if __name__=='__main__':

    # Parsing CL args to get grid, tunnel and phases params
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", help = "Size of grid", type = int, default = N_DEFAULT)
    parser.add_argument("-k", help = "Max size of tunnel", type = int, default = K_DEFAULT)
    parser.add_argument("-p", help = "Number of detection phases", type = int, default = P_DEFAULT)
    args = parser.parse_args()
    

    print_wait()
    flask_app.run(host = hostname, port = port)
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
import argparse

flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(flask_app)

hostname = '0.0.0.0'
port = 8080

# Some default game params
N_DEFAULT = 5
K_DEFAULT = 9
P_DEFAULT = 3

# Keeping tabs on tunneler and detector
tunneler = {}
detector = {}

@socketio.on('message')
def handle_message(data):
    print("Received message: " + data)

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

    if("reg" in tunneler and "reg" in detector):
        # Tunneler's initial phase starts here
        start_game()
    
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

def start_game():
    print("Game has begun\n")
    # Start the tunneler's timer here

if __name__=='__main__':

    # Parsing CL args to get grid, tunnel and phases params
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", help = "Size of grid", type = int, default = N_DEFAULT)
    parser.add_argument("-k", help = "Max size of tunnel", type = int, default = K_DEFAULT)
    parser.add_argument("-p", help = "Number of detection phases", type = int, default = P_DEFAULT)
    args = parser.parse_args()
    

    print_wait()
    socketio.run(flask_app, host = hostname, port = port)
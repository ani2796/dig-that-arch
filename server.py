from flask import Flask, jsonify, request
import argparse


flask_app = Flask(__name__)
hostname = '0.0.0.0'
port = 8080

# Some default game params
N_DEFAULT = 5
K_DEFAULT = 9
P_DEFAULT = 3

@flask_app.route('/registration', methods=['GET'])
def register():
    print("Registering name: ", request.args.get("name"))
    return jsonify({
        "n": args.n,
        "k": args.k,
        "p": args.p
    })

if __name__=='__main__':

    # Parsing CL args to get grid, tunnel and phases params
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", help = "Size of grid", type = int, default = N_DEFAULT)
    parser.add_argument("-k", help = "Max size of tunnel", type = int, default = K_DEFAULT)
    parser.add_argument("-p", help = "Number of detection phases", type = int, default = P_DEFAULT)
    args = parser.parse_args()
    
    flask_app.run(host = hostname, port = port)
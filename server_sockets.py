import asyncio
import websockets
import argparse
import json
import time

from server_rest import register


hostname = "localhost"
port = 8080

# Some default game params
N_DEFAULT = 5
K_DEFAULT = 9
P_DEFAULT = 3

tunneler = {}
detector = {}
connected = set()
args = None

async def echo(websocket, path):
    async for message in websocket:
        await websocket.send(message)

async def hello(websocket, path):
    name = await websocket.recv()
    print(f"<<< {name}")

    greeting = f"Hello, {name}."

    await websocket.send(greeting)
    print(f"<<< {greeting}")
    
async def main():
    # Parsing command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", help = "Size of grid", type = int, default = N_DEFAULT)
    parser.add_argument("-k", help = "Max size of tunnel", type = int, default = K_DEFAULT)
    parser.add_argument("-p", help = "Number of detection phases", type = int, default = P_DEFAULT)
    global args
    args = parser.parse_args()
    print("Done parsing args")

    async with websockets.serve(evaluator, hostname, port):
        await asyncio.Future()

async def evaluator(websocket, path):    
    init_msg = json.loads(await websocket.recv())
    print("Initial message: " + str(init_msg))
    role = init_msg["role"]
    name = init_msg["name"]

    if(role == "Tunneler"):
        start_msg = json.dumps({"canStart": True, "n": args.n, "k": args.k, "p": args.p})
        await websocket.send(start_msg)
        # start timer here
        path_msg = json.loads(await websocket.recv())
        # stop timer here
        print("Message sent by tunneler: " + str(path_msg))

    elif(role == "Detector"):
        start_msg = json.dumps({"n": args.n, "k": args.k, "p": args.p})
        await websocket.send(start_msg)

        for i in range(1, args.p + 1):
            round_msg = json.dumps({"round": i})
            await websocket.send(round_msg)
            #start timer here
            guess = json.loads(await websocket.recv())
            # stop timer here
            # evaluate guess
            print("Detector sent guess: " + str(guess))
            result = json.dumps({"edge": True})
            await websocket.send(result)

def path_validate(path_msg):
    points = path_msg["edges"]
    print("Edge data: " + str(points))
    return True

def register_clients(message):
    data = json.loads(message)
    
    role = data.get("role")
    name = data.get("name")

    if(not name or not role):
        return "Please send both name and role (Detector/Tunneler)", role, 412
    elif(not (role == "Tunneler" or role == "Detector")):
        return "Invalid role: please send either Detector or Tunneler", role, 412
    elif(role == "Tunneler" and "reg" in tunneler):
        return "Tunneler role already taken", role, 412
    elif(role == "Detector" and "reg" in detector):
        return "Detector role already taken", role, 412
    
    if(role == "Tunneler"):
        tunneler["reg"] = name
    elif(role == "Detector"):
        detector["reg"] = name
    return "Successfully registered " + role, role, 200

asyncio.run(main())
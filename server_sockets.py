import asyncio
import websockets
import argparse
import json

from server_rest import register


hostname = "localhost"
port = 8080

# Some default game params
N_DEFAULT = 5
K_DEFAULT = 9
P_DEFAULT = 3

tunneler = {}
detector = {}

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
    async with websockets.serve(get_cl_args, hostname, port):
        await asyncio.Future()

async def get_cl_args(websocket, path):
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", help = "Size of grid", type = int, default = N_DEFAULT)
    parser.add_argument("-k", help = "Max size of tunnel", type = int, default = K_DEFAULT)
    parser.add_argument("-p", help = "Number of detection phases", type = int, default = P_DEFAULT)
    args = parser.parse_args()
    print("Command line args obtained", str(args.n), str(args.k), str(args.p))

    async for message in websocket:
        msg, code = register_clients(message)
        json_msg = json.dumps({"msg": msg, "code": code})
        await websocket.send(json_msg)
        print("Message sent to websocket!")


def register_clients(message):
    data = json.loads(message)
    
    role = data.get("role")
    name = data.get("name")

    if(not name or not role):
        return "Please send both name and role (Detector/Tunneler)", 412
    elif(not (role == "Tunneler" or role == "Detector")):
        return "Invalid role: please send either Detector or Tunneler", 412
    elif(role == "Tunneler" and "reg" in tunneler):
        return "Tunneler role already taken", 412
    elif(role == "Detector" and "reg" in detector):
        return "Detector role already taken", 412
    else:
        return "Successfully registered " + role, 200

asyncio.run(main())
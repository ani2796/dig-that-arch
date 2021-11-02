import asyncio
import websockets
import json

hostname = "0.0.0.0"
port = 8080

# Regsitering with the server as the tunneler
async def build_tunnel():
    async with websockets.connect("ws://" + hostname + ":" + str(port)) as websocket:
        await websocket.send(json.dumps({"name": "PythonClient", "role": "Tunneler"}))
        
        start_msg = json.loads(await websocket.recv())
        if(start_msg["canStart"]):
            path_msg = json.dumps({"name": "PythonClient", "edges": tunnel_edges()})
            await websocket.send(path_msg)

def tunnel_edges():
    sample_3x3 = ( [(0, 0), (0, 1)], [(0, 1), (1, 1)], [(1, 1), (1, 2)], [(1, 2), (2, 2)], [(2, 2), (2, 3)])
    return sample_3x3

asyncio.run(build_tunnel())
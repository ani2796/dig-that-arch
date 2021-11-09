import asyncio
import websockets
import json

hostname = "127.0.0.1"
port = 8081
client_name = "PythonClient"
count = 0

# Building tunnel
async def build_tunnel():
    async with websockets.connect("ws://" + hostname + ":" + str(port)) as websocket:
        result = {"tunneling_done": False}

        # Initial message registering client with server
        await websocket.send(json.dumps({"name": client_name, "role": "Tunneler"}))
        # Receiving params from server: n, p, k
        params = json.loads(await websocket.recv())

        while True:
            # Receiving signal to start from server
            start_msg = json.loads(await websocket.recv())

            path_msg = json.dumps({"name": client_name, "edges": tunnel_edges(params, result)})
            await websocket.send(path_msg)
            result = json.loads(await websocket.recv())
            if(result["tunneling_done"]):
                break

def tunnel_edges(params, result):

    # Insert your logic here and return the path
    # Remember that the server will wait until you send a valid path
    # You can check the "tunneling_done" param of the "result" variable

    # Sample format for tunnel edges
    sample_3x3 = ( [(0, 0), (0, 1)], [(1, 1), (0, 1)], [(1, 1), (1, 2)], [(2, 2), (1, 2)], [(2, 2), (2, 3)], [(3, 3), (2, 3)], [(3, 3), (3, 4)])
    return sample_3x3
asyncio.run(build_tunnel())
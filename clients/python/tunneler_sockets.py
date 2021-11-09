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
    sample_5x5 = ([[0, 5], [0, 4]], [[0, 4], [1, 4]], [[1, 4], [1, 3]], [[0, 3], [1, 3]], [[0, 3], [0, 2]], [[0, 2], [0, 1]], [[0, 1], [0, 0]], [[0, 0], [1, 0]], [[1, 0], [2, 0]], [[2, 0], [2, 1]], [[2, 1], [2, 2]], [[2, 2], [2, 3]], [[2, 3], [2, 4]], [[2, 4], [2, 5]], [[2, 5], [3, 5]], [[3, 5], [4, 5]], [[4, 5], [5, 5]], [[5, 5], [5, 4]], [[5, 4], [4, 4]], [[4, 4], [4, 3]], [[4, 3], [5, 3]], [[5, 3], [5, 2]], [[5, 2], [4, 2]], [[4, 2], [4, 1]], [[4, 1], [5, 1]], [[5, 1], [5, 0]])
    return sample_5x5
asyncio.run(build_tunnel())
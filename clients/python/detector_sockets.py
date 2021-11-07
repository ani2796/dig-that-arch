import asyncio
import websockets
import json

hostname = "127.0.0.1"
port = 8081
client_name = "PythonClient"

# Detecting tunnel
async def detect_tunnel():
    async with websockets.connect("ws://" + hostname + ":" + str(port)) as websocket:
        await websocket.send(json.dumps({"name": client_name, "role": "Detector"}))
        params = json.loads(await websocket.recv())
        print("Params recvd from server:" + str(params))

        for i in range(1, params["p"] + 1):
            # Receiving round number from server
            round = json.loads(await websocket.recv())
            print("Round: " + str(round))

            # Insert your code here

            # Sample guess containing edges and vertices
            guess = json.dumps({"name": client_name, "edges": [[(0, 1), (0, 0)], [(0, 1), (1, 1)], [(1, 3), (1, 2)]], "vertices": [(0, 0), (0, 1), (1, 1), (2, 3)]})
            
            # Getting back the edges from the server that match the tunneler's path
            await websocket.send(guess)
            result = json.loads(await websocket.recv())
            print("Result from server: " + str(result))
        

        # Insert your code here

        # Sending final guess to the server
        final_guess = json.dumps({"edges": [[(0, 0), (0, 1)], [(0, 1), (1, 1)], [(1, 1), (1, 2)], [(1, 2), (2, 2)], [(2, 2), (2, 3)]]})
        await websocket.send(final_guess)


asyncio.run(detect_tunnel())
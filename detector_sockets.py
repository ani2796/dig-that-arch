import asyncio
import websockets
import json

hostname = "0.0.0.0"
port = 8080

async def registration():
    async with websockets.connect("ws://" + hostname + ":" + str(port)) as websocket:
        await websocket.send(json.dumps({"name": "PythonClient2", "role": "Detector"}))
        start_msg = json.loads(await websocket.recv())

        for i in range(1, start_msg["p"] + 1):
            round = json.loads(await websocket.recv())
            print("Round: " + str(round))
            guess = json.dumps({"round": "this is a round"})
            await websocket.send(guess)
            result = json.loads(await websocket.recv())
            print("Evaluated result for round: " + str(result))

asyncio.get_event_loop().run_until_complete(registration())
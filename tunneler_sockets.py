import asyncio
import websockets
import json

hostname = "0.0.0.0"
port = 8080

async def registration():
    async with websockets.connect("ws://" + hostname + ":" + str(port)) as websocket:
        await websocket.send(json.dumps({"name": "PythonClient", "role": "Tunneler"}))
        json_dump = await websocket.recv()
        print("Server response: " + str(json_dump))


asyncio.get_event_loop().run_until_complete(registration())
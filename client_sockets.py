import asyncio
import websockets

hostname = "localhost"
port = 8080

async def hello():
    async with websockets.connect("ws://localhost:8080") as websocket:
        name = input("What's your name?")
        await websocket.send(name)
        
        print(f">>> {name}")

        greeting = await websocket.recv()
        print(f"<<< {greeting}")

asyncio.run(hello())
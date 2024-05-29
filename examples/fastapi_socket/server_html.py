from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

clients = []

async def handle_websocket(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received: {data}")
            for client in clients:
                await client.send_text(f"Server received: {data}")
    except WebSocketDisconnect:
        clients.remove(websocket)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await handle_websocket(websocket)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}

# main.py
import socket
import threading
from fastapi import FastAPI, HTTPException
from typing import List

app = FastAPI()

connections = []

def handle_client_connection(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Received message: {message}")
            client_socket.send(f"Server received: {message}".encode('utf-8'))
        except ConnectionResetError:
            break
    client_socket.close()

def start_socket_server(port: int):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind(("127.0.0.1", port))
        print(f"Socket server started on port {port}")
    except OSError as e:
        # if e.errno == 98:  # Address already in use
        #     new_port = port + 1
        #     return start_socket_server(new_port)
        # else:
        #     raise e
        # for simplcity, maunally resolve the port conflict.
        # Note: when using nginx, it might not release the binded port after server shutdown,
        # Causing port conflict if immediately restarting the server.
        raise OSError(f"{e}. When Socket server starting on port {port}." ) 
    server_socket.listen(5)

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        client_thread = threading.Thread(target=handle_client_connection, args=(client_socket,))
        client_thread.start()

@app.on_event("startup")
async def startup_event():
    socket_thread = threading.Thread(target=start_socket_server, args=(9000,))
    socket_thread.start()

@app.get("/")
def read_root():
    return {"message": "FastAPI server with socket handling"}

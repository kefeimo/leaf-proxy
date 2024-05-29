from fastapi import FastAPI
import socket
import threading

app = FastAPI()

HOST = '127.0.0.1'
PORT = 65432  # Starting port

# Function to handle client connection
def handle_client(conn, addr):
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Received from {addr}: {data.decode()}")
            conn.sendall(data)

# Function to start the socket server
def start_socket_server():
    global PORT
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, PORT))
                s.listen()
                print(f"Socket server listening on {HOST}:{PORT}")
                while True:
                    conn, addr = s.accept()
                    threading.Thread(target=handle_client, args=(conn, addr)).start()
        except OSError as e:
            if e.errno == 98:  # Address already in use
                PORT += 1
                print(f"Port {PORT - 1} in use, trying port {PORT}")
            else:
                raise

@app.on_event("startup")
def startup_event():
    threading.Thread(target=start_socket_server).start()

# Start FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

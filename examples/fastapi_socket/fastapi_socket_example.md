# fastapi socket example

Let's create a simple example using FastAPI for the server and a Python socket for the client. We'll handle the **`OSError: [Errno 98] Address already in use`** error by trying to bind to the next available port if the default port is already in use.

### **Server Side (FastAPI)**

First, we'll set up a FastAPI server that listens for connections and communicates with clients using sockets.

1. Install FastAPI and Uvicorn:
    
    ```bash
    bashCopy code
    pip install fastapi uvicorn
    
    ```
    
2. Create the server code:

```python
pythonCopy code
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

```

### **Client Side**

Now, let's create the client that connects to the server, takes user input, and prints the server response.

1. Create the client code:

```python
pythonCopy code
import socket
import threading

HOST = '127.0.0.1'
PORT = 65432  # Starting port, make sure this matches the server's port

def receive_data(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            break
        print(f"Received from server: {data.decode()}")

def main():
    global PORT
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                print(f"Connected to server on port {PORT}")

                # Start thread to receive data
                threading.Thread(target=receive_data, args=(s,)).start()

                while True:
                    msg = input("Enter message to send: ")
                    s.sendall(msg.encode())

        except ConnectionRefusedError:
            PORT += 1
            print(f"Connection refused on port {PORT - 1}, trying port {PORT}")
        except OSError as e:
            if e.errno == 98:  # Address already in use
                PORT += 1
                print(f"Port {PORT - 1} in use, trying port {PORT}")
            else:
                raise

if __name__ == "__main__":
    main()

```

### **Running the Example**

1. Run the FastAPI server:
    
    ```bash
    bashCopy code
    python server.py
    
    ```
    
2. Run the client:
    
    ```bash
    bashCopy code
    python client.py
    
    ```
    

### **Explanation**

- **Server Side**:
    - We create a FastAPI app and start a socket server in a separate thread on startup.
    - The socket server listens for connections and handles each connection in a separate thread.
    - If the port is in use, it increments the port number and tries again.
- **Client Side**:
    - The client attempts to connect to the server on a specified port.
    - If the connection is refused or the port is in use, it increments the port number and tries again.
    - It takes user input and sends it to the server, and starts a thread to print out responses from the server.

This setup ensures the client maintains a persistent connection to the server and handles the "Address already in use" error by trying the next available port.
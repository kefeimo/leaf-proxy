# tcp chat in python

Below is a complete example of a TCP chat application using Python's **`socket`** and **`threading`** modules, following the architecture and explanation provided in your content. The example includes both the server-side and client-side code.

ref: https://www.neuralnine.com/tcp-chat-in-python/

### **Server-Side Code (server.py)**

```python
pythonCopy code
import socket
import threading

# Connection Data
host = '127.0.0.1'
port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
nicknames = []

# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Handling Messages From Clients
def handle(client):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024)
            broadcast(message)
        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast('{} left!'.format(nickname).encode('ascii'))
            nicknames.remove(nickname)
            break

# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        broadcast("{} joined!".format(nickname).encode('ascii'))
        client.send('Connected to server!'.encode('ascii'))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server is listening...")
receive()

```

### **Client-Side Code (client.py)**

```python
pythonCopy code
import socket
import threading

# Choosing Nickname
nickname = input("Choose your nickname: ")

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

# Listening to Server and Sending Nickname
def receive():
    while True:
        try:
            # Receive Message From Server
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            # Close Connection When Error
            print("An error occurred!")
            client.close()
            break

# Sending Messages To Server
def write():
    while True:
        message = '{}: {}'.format(nickname, input(''))
        client.send(message.encode('ascii'))

# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

```

### **Explanation of Code**

### **Server-Side Code**

1. **Connection Data**:
    - **`host`**: The IP address the server will listen on.
    - **`port`**: The port number the server will listen on.
2. **Starting Server**:
    - **`server`**: Creates a socket object.
    - **`server.bind((host, port))`**: Binds the server to the host and port.
    - **`server.listen()`**: Starts the server in listening mode.
3. **Broadcast Function**:
    - **`broadcast(message)`**: Sends a message to all connected clients.
4. **Handle Function**:
    - Handles incoming messages from clients and broadcasts them. If an error occurs, it removes the client and closes the connection.
5. **Receive Function**:
    - Accepts new connections, requests nicknames, and starts a new thread to handle each client.

### **Client-Side Code**

1. **Choosing Nickname**:
    - **`nickname`**: The user's chosen nickname.
2. **Connecting To Server**:
    - **`client`**: Creates a socket object.
    - **`client.connect(('127.0.0.1', 55555))`**: Connects to the server at the given IP and port.
3. **Receive Function**:
    - Receives messages from the server. If the message is **`NICK`**, it sends the nickname to the server. Otherwise, it prints the message.
4. **Write Function**:
    - Takes user input, formats it with the nickname, and sends it to the server.
5. **Starting Threads**:
    - Starts two threads, one for receiving messages and one for writing messages.

### **Running the Chat Application**

1. **Start the Server**:
    - Run **`server.py`** first to start the server.
    - Command: **`python server.py`**
2. **Start the Clients**:
    - Run **`client.py`** in separate terminals or on separate machines to start the clients.
    - Command: **`python client.py`**

Each client can then communicate with others through the server. Messages from any client will be broadcasted to all other connected clients.

![Untitled](tcp%20chat%20in%20python/Untitled.png)
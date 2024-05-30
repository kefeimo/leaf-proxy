# fastapi socket example with nginx for stream connection

### **How to Run the Code**

1. **Start the FastAPI Server**:
    - Install fastapi and uvicorn
    - Save the server code to a file named **`main.py`**.
        
        ```python
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
        
        ```
        
    - Run the server using **`uvicorn`**:This will start the FastAPI server on port 8000 and the socket server on port 9000.
        
        ```bash
        uvicorn main:app --host 0.0.0.0 --port 8000
        
        ```
        
2. **Configure NGINX**:
    - Add the NGINX configuration to your NGINX configuration file, typically located at **`/etc/nginx/nginx.conf`**.
        
        ```bash
        # /etc/nginx/nginx.conf
        user nginx;
        worker_processes auto;
        error_log /var/log/nginx/error.log;
        pid /var/run/nginx.pid;
        
        events {
            worker_connections 1024;
        }
        
        stream {
            upstream tcp_backend {
                server 127.0.0.1:9000;  # the address server hosts
            }
        
            server {
                listen 9500;
                proxy_pass tcp_backend;
                proxy_timeout 600s;
                proxy_connect_timeout 10s;
            }
        }
        ```
        
    - Restart NGINX to apply the configuration:
        
        ```bash
        sudo nginx -t
        sudo systemctl restart nginx
        
        ```
        
    - Note: see appendix for common issue when running nginx server for streaming
        - how to fix “nginx: [emerg] unknown directive "stream" in /etc/nginx/nginx.conf”
        - how to fix "[emerg] getpwnam("nginx") failed in /etc/nginx/nginx.conf”
3. **Start the Client**:
    - Save the client code to a file named **`client.py`**.
        
        ```python
        # client.py
        import socket
        
        def start_client(host: str, port: int):
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
        
            try:
                while True:
                    message = input("Enter message to send to server: ")
                    if message.lower() == 'exit':
                        break
                    client_socket.send(message.encode('utf-8'))
                    response = client_socket.recv(1024).decode('utf-8')
                    print(f"Received from server: {response}")
            except KeyboardInterrupt:
                print("Client disconnected.")
            finally:
                client_socket.close()
        
        if __name__ == "__main__":
            # start_client("localhost", 9000)  # for testing without nginx
            start_client("127.0.0.1", 9500) # for testing with nginx
        
        ```
        
    - Run the client using Python:
        
        ```bash
        python client.py
        
        ```
        
    - The client connects to the server on port 9500, which is routed by NGINX to port 9000.

### **Server Logs Analysis**

```bash
$ uvicorn main:app
INFO:     Started server process [578314]
INFO:     Waiting for application startup.
Socket server started on port 9000
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
Accepted connection from ('127.0.0.1', 33130)
Accepted connection from ('127.0.0.1', 39034)
Received message: sdssd

```

- **INFO logs**: Indicate that the FastAPI server and socket server are running.
- **Socket server started on port 9000**: Confirms the socket server is listening on port 9000.
- **Accepted connection from**: Shows that clients have connected to the socket server.
- **Received message**: Logs the message received from the client.

This setup illustrates how NGINX can be used to route TCP traffic between different ports and how it integrates with a FastAPI server and a custom socket server.

### (Optional) Verification

**1. Running the Echo Server Without NGINX (expected to succeed)**

- Start the FastAPI server (which also starts the socket server on port 9000).
- Run the client code with **`start_client("127.0.0.1", 9000)`** to connect directly to the socket server.
- This step demos the expected behavior of the echo server.
    
    ![Untitled](fastapi%20socket%20example%20with%20nginx%20for%20stream%20conne/Untitled.png)
    

 **1b. Running the Echo Server Without NGINX (expected to fail)**

- Change the port to 10000 (or some other arbitrary port number) then inspect the connect fail as expected.
    
    ```bash
    $ python playground/client.py 
    Traceback (most recent call last):
      File "/home/kefei/project/leaf-proxy/playground/client.py", line 23, in <module>
        start_client("127.0.0.1", 10000) # for testing with nginx
      File "/home/kefei/project/leaf-proxy/playground/client.py", line 6, in start_client
        client_socket.connect((host, port))
    ConnectionRefusedError: [Errno 111] Connection refused
    ```
    

**2. Running the Echo Server With NGINX (expected to succeed)**

- Start the FastAPI server (which also starts the socket server on port 9000).
- Start the nginx server (`sudo systemctl restart nginx` and verify with `sudo systemctl status nginx`)
- Run the client code with **`start_client("127.0.0.1", 9500)`** to connect to the socket server through proxy.

**2b. Running the Echo Server With NGINX (expected to fail)**

- Stop the nginx server (`sudo systemctl stop nginx`)
- Run the client code with **`start_client("127.0.0.1", 9500)`** to connect to the socket server through proxy, inspect the connect fail as expected.
    
    ```bash
    $ python playground/client.py 
    Traceback (most recent call last):
      File "/home/kefei/project/leaf-proxy/playground/client.py", line 23, in <module>
        start_client("127.0.0.1", 9500) # for testing with nginx
      File "/home/kefei/project/leaf-proxy/playground/client.py", line 6, in start_client
        client_socket.connect((host, port))
    ConnectionRefusedError: [Errno 111] Connection refused
    ```
    

### Q&A

**How the Echo Server Works Without the NGINX Proxy Server**

Without NGINX, the socket server runs on port 9000 and the FastAPI server runs on port 8000. The **`start_socket_server`** function initializes a TCP socket server that listens for incoming connections on port 9000. When a client connects, it spawns a new thread to handle the client connection, allowing for multiple concurrent connections.

**Relationship Between Port 8000 and 9000**

- **Port 8000**: This is where the FastAPI application listens for HTTP requests. It's used for serving FastAPI routes, such as the root endpoint that returns a JSON message.
- **Port 9000**: This is where the custom socket server listens for raw TCP connections. It handles the echo functionality, where it receives messages from the client and sends back a response.

**Role of NGINX**

NGINX acts as a reverse proxy and load balancer, which can forward requests to different backend services. In this setup, NGINX reroutes TCP traffic from one port to another.

**How It Reroutes the Port from 9500 to 9000**

In the NGINX configuration, the **`stream`** block is used to handle TCP traffic. It listens on port 9500 and forwards any incoming connections to the backend server running on port 9000.

**How It Is Reflected in the NGINX Configuration**

Here is the NGINX configuration:

```
# /etc/nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

stream {
    upstream tcp_backend {
        server 127.0.0.1:9000;  # the address server hosts
    }

    server {
        listen 9500;  # NGINX listens on this port
        proxy_pass tcp_backend;  # forwards traffic to tcp_backend (port 9000)
        proxy_timeout 600s;
        proxy_connect_timeout 10s;
    }
}

```

**Detailed Explanation of Code and Logs**

- **Server Code**:
    - **`start_socket_server`**: Initializes the socket server, binds to port 9000, and listens for connections.
    - **`handle_client_connection`**: Handles incoming messages from clients and sends back an echo response.
- **Client Code**:
    - **`start_client`**: Connects to the specified host and port (127.0.0.1:9500), sends user input to the server, and prints the server's response.
- **NGINX Configuration**:
    - **`stream { upstream tcp_backend { server 127.0.0.1:9000; } }`**: Defines the upstream server.
    - **`server { listen 9500; proxy_pass tcp_backend; }`**: Listens on port 9500 and forwards connections to the upstream server on port 9000.

### Common Nginx issues:

**How to fix nginx: [emerg] unknown directive "stream" in /etc/nginx/nginx.conf”**

The error message **`nginx: [emerg] unknown directive "stream"`** indicates that the Stream module is not enabled in your NGINX build. To fix this, you have a few options:

1. **Install NGINX with the Stream module**: Ensure that you are using a version of NGINX that includes the Stream module. The official NGINX repository provides versions with this module included.
2. **Use dynamic module loading**: If you are using a version of NGINX that supports dynamic modules, you might need to load the Stream module dynamically.

### **Option 1: Install NGINX with the Stream Module**

The easiest way to ensure you have the Stream module is to install NGINX from the official repositories. Here are the steps for installing it on a Debian-based system (like Ubuntu):

1. **Add the NGINX official repository**:
    
    ```bash
    sudo apt update
    sudo apt install curl gnupg2 ca-certificates lsb-release
    echo "deb http://nginx.org/packages/ubuntu $(lsb_release -cs) nginx" | sudo tee /etc/apt/sources.list.d/nginx.list
    curl -fsSL https://nginx.org/keys/nginx_signing.key | sudo apt-key add -
    sudo apt update
    
    ```
    
2. **Install NGINX**:
    
    ```bash
    sudo apt install nginx
    
    ```
    

This version of NGINX should include the Stream module by default.

### **Option 2: Load the Stream Module Dynamically**

If your version of NGINX supports dynamic modules, you can load the Stream module dynamically by adding the following line to your **`nginx.conf`** file before using the **`stream`** directive:

```
load_module /usr/lib/nginx/modules/ngx_stream_module.so;

```

### **Updated NGINX Configuration**

Here's how your updated **`nginx.conf`** file should look with the module loaded dynamically:

```
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /var/run/nginx.pid;

load_module /usr/lib/nginx/modules/ngx_stream_module.so;

events {
    worker_connections 1024;
}

stream {
    upstream tcp_backend {
        server 127.0.0.1:9500;
    }

    server {
        listen 9000;
        proxy_pass tcp_backend;
        proxy_timeout 600s;
        proxy_connect_timeout 10s;
    }
}

```

### **Verify the Stream Module**

You can verify that the Stream module is available and loaded by running:

```bash
nginx -V 2>&1 | grep -o with-stream

```

If the module is available, you should see **`with-stream`** in the output.

### **Final Steps**

1. **Test the NGINX configuration**:
    
    ```bash
    sudo nginx -t
    
    ```
    
2. **Restart NGINX**:
    
    ```bash
    sudo systemctl restart nginx
    ```
    

**How to fix "[emerg] getpwnam("nginx") failed in /etc/nginx/nginx.conf”**

The error **`[emerg] getpwnam("nginx") failed in /etc/nginx/nginx.conf`** indicates that the NGINX user specified in the configuration file does not exist on your system. This can happen if the **`nginx`** user was not created during the installation process.

To fix this error, you have a few options:

### **Option 1: Create the `nginx` User**

1. **Create the `nginx` user**:
    
    ```bash
    bashCopy code
    sudo useradd -r -d /var/cache/nginx -s /sbin/nologin -U nginx
    
    ```
    
    - **`r`**: Create a system account.
    - **`d /var/cache/nginx`**: Set the home directory.
    - **`s /sbin/nologin`**: Disable login for this user.
    - **`U`**: Create a group with the same name as the user.
2. **Verify that the user was created**:
    
    ```bash
    bashCopy code
    id nginx
    
    ```
    
    This command should output information about the **`nginx`** user if it was created successfully.
    

### **Option 2: Use an Existing User**

If you don't want to create a new user, you can modify the **`nginx.conf`** to use an existing user, such as **`www-data`** (commonly used for web servers).

1. **Modify `nginx.conf`**:
    
    ```
    nginxCopy code
    # /etc/nginx/nginx.conf
    user www-data;
    worker_processes auto;
    error_log /var/log/nginx/error.log;
    pid /var/run/nginx.pid;
    
    events {
        worker_connections 1024;
    }
    
    stream {
        upstream tcp_backend {
            server 127.0.0.1:9500;
        }
    
        server {
            listen 9000;
            proxy_pass tcp_backend;
            proxy_timeout 600s;
            proxy_connect_timeout 10s;
        }
    }
    
    ```
    

### **Option 3: Install NGINX Correctly**

Ensure NGINX is installed correctly, which typically involves the creation of the **`nginx`** user automatically.

1. **Reinstall NGINX**:
    
    ```bash
    sudo apt-get remove nginx nginx-core
    sudo apt-get install nginx
    
    ```
    

### **Verifying and Restarting NGINX**

After making any changes, test the NGINX configuration to ensure it’s valid:

```bash
sudo nginx -t
```

If the test is successful, restart NGINX:

```bash
sudo systemctl restart nginx
```

### **Example Configuration with `www-data`**

If you chose to use the **`www-data`** user, your configuration file would look like this:

```
# /etc/nginx/nginx.conf
user www-data;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

stream {
    upstream tcp_backend {
        server 127.0.0.1:9500;
    }

    server {
        listen 9000;
        proxy_pass tcp_backend;
        proxy_timeout 600s;
        proxy_connect_timeout 10s;
    }
}

```

By following these steps, you should be able to resolve the **`getpwnam("nginx") failed`** error and successfully start NGINX with your desired configuration.
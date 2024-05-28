# nginx python server

Here's a basic example of how to use Nginx as a reverse proxy to forward requests to a Python server implemented using the **`socket`** and **`threading`** modules.

### **Step 1: Install Nginx**

If you haven't already installed Nginx, you can do so using your package manager. For example, on Ubuntu:

```bash
bashCopy code
sudo apt update
sudo apt install nginx

```

### **Step 2: Configure Nginx**

Create a new configuration file for your server. For example, create a file called **`myapp.conf`** in the **`/etc/nginx/sites-available/`** directory with the following content:

```
nginxCopy code
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

```

Then enable this configuration by creating a symbolic link to it in the **`/etc/nginx/sites-enabled/`** directory:

```bash
bashCopy code
sudo ln -s /etc/nginx/sites-available/myapp.conf /etc/nginx/sites-enabled/

```

Finally, restart Nginx to apply the changes:

```bash
bashCopy code
sudo systemctl restart nginx

```

### **Step 3: Create a Simple Python Server**

Here is a basic Python server using **`socket`** and **`threading`**. Save this script as **`simple_server.py`**.

```python
pythonCopy code
import socket
import threading

def handle_client(client_socket):
    request = client_socket.recv(1024).decode('utf-8')
    print(f"Received: {request}")

    http_response = """\
HTTP/1.1 200 OK

Hello from Python server!
"""
    client_socket.sendall(http_response.encode('utf-8'))
    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8000))
    server.listen(5)
    print("Server listening on port 8000")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    main()

```

### **Step 4: Run the Python Server**

Run your Python server script:

```bash
bashCopy code
python3 simple_server.py

```

### **Step 5: Test the Setup**

With both Nginx and your Python server running, you can now access your server through Nginx. Open your web browser and navigate to **`http://your_domain_or_ip`**. (Note: using wsl with vscode allows easily access the server through “localhost:8000”). You should see the message "Hello from Python server!" displayed, which indicates that Nginx is successfully proxying requests to your Python server.

This setup demonstrates a simple reverse proxy with Nginx forwarding requests to a Python server. In a real-world scenario, you would likely use a more robust Python web framework such as Flask or Django and configure Nginx with additional settings for security, caching, and load balancing.
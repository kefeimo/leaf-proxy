# Example: Using Nginx with FastAPI in Python for an Echo Server

**Example: Using Nginx with FastAPI in Python for an Echo Server**

This example demonstrates how to set up an echo server using FastAPI with Nginx acting as a reverse proxy. Nginx will handle incoming requests on port 80 and forward them to the FastAPI server running on port 8000. We will use the IP address `192.168.0.1` .

Note: you can use `ip addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'` to check the ip from the wsl machine. (ref: [**How to find WSL2 machine's IP address from windows](https://superuser.com/questions/1586386/how-to-find-wsl2-machines-ip-address-from-windows))**

### **Step-by-Step Implementation**

### **1. FastAPI Echo Server**

First, create the FastAPI server. Save this as **`fastapi_echo.py`**.

```python
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/echo")
async def echo(request: Request):
    data = await request.body()
    return {"received_data": data.decode('utf-8')}
    
@app.get("/echo")
async def echo_get(data: str = Query(None)):
    return {"received_data_get": data}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

This server listens for POST requests and the GET query at the **`/echo`** endpoint and echoes the received data back to the client.

### **2. Nginx Configuration**

Next, configure Nginx to act as a reverse proxy. Create or edit the Nginx configuration file at **`/etc/nginx/sites-available/fastapi_echo`**.

```
server {
    listen 80;
    server_name 192.168.0.1;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site by creating a symbolic link in the **`sites-enabled`** directory and restart Nginx.

```bash
sudo ln -s /etc/nginx/sites-available/fastapi_echo /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### **3. Start the FastAPI Server**

Run the FastAPI server using Uvicorn.

```bash
python fastapi_echo.py
```

### **4. Client (Vendor Side) (optional)**

Create a Python script to act as the client, which will send data to the FastAPI echo server through the Nginx proxy.

Save this script as **`vendor_client.py`**.

```python
import requests

url = "http://192.168.0.1/echo"

# Data to be sent in the POST request
data = "Hello, FastAPI via Nginx!"

response = requests.post(url, data=data, headers={"Content-Type": "text/plain"})

print(response.json())

```

This script sends a POST request to the echo server via the Nginx proxy and prints the response.

### **Running the Setup**

1. **Start the FastAPI Server**:
    
    ```bash
    python fastapi_echo.py
    
    ```
    
2. **Ensure Nginx is Running**:
    
    ```bash
    sudo systemctl restart nginx
    ```
    
3. (optional) **Run the Client Script**: 
    
    ```bash
    python vendor_client.py
    ```
    
4. **(alternative) Run the curl command**
    
    ```bash
    curl -X POST "http://192.168.0.1/echo"  --data "sending test"
    
    curl "http://192.168.0.1/echo?data=Hello%20FastAPI%22"
    ```
    
5. **(alternative) Run from the browser**
    
    ```bash
    http://192.168.0.1/echo?data=Hello%20FastAPI%22
    ```
    

### **Explanation of the Flow**

1. **Client (Vendor Side)**:
    - The client script sends a POST request to **`http://**192.168.0.1**/echo**` with some data.
2. **Nginx**:
    - Nginx listens for incoming requests on port 80.
    - When Nginx receives the request, it forwards it to the FastAPI server running on **`127.0.0.1:8000`**.
3. **Uvicorn (FastAPI Server)**:
    - Uvicorn receives the forwarded request on port 8000.
    - The FastAPI application processes the request, extracts the data, and sends a response back to Nginx.
4. **Nginx**:
    - Nginx receives the response from the FastAPI server.
    - Nginx forwards the response back to the client.
5. **Client Receives Response**:
    - The client script receives and prints the response, showing the echoed data.

### Verification

Note: use `sudo systemctl status nginx` to check the status of the nginx server. Use `sudo systemctl stop nginx` to stop it. And `sudo systemctl restart nginx` to (re)start it otherwise.

With the following simple experiment, we can verify if nginx proxy server is serving as expected. 

When serving:

```bash
(fastapi) kefei@WE44933:~/project/leaf-proxy/examples/solid_example$ curl "http://192.168.0.1/echo?data=Hello%20FastAPI%22"
>> {"received_data_get":"Hello FastAPI\""}
```

When stopped:

```bash
(fastapi) kefei@WE44933:~/project/leaf-proxy/examples/solid_example$ curl "http://192.168.0.1/echo?data=Hello%20FastAPI%22"
>> curl: (7) Failed to connect to 192.168.0.1 port 80 after 0 ms: Connection refused

(fastapi) kefei@WE44933:~/project/leaf-proxy/examples/solid_example$ curl "localhost:8000/echo?data=Hello%20FastAPI%22"
>> {"received_data_get":"Hello FastAPI\""}(fastapi)
```

In summary, when the Nginx proxy is operational, it effectively reroutes requests from port 80 to port 8000 as specified in the configuration. However, in its absence, port 80 remains unresponsive, necessitating direct queries to **`localhost:8000`** where the server is hosted.

### **Role of Nginx**

- **Reverse Proxy**: Nginx acts as a reverse proxy, forwarding requests from the public-facing IP address (`192.168.0.1`) to the internal FastAPI server.
- **Load Balancing**: Although not used in this simple example, Nginx can distribute incoming requests to multiple instances of the FastAPI server for better load management.
- **Security and Performance**: Nginx can handle connection management, reduce latency, and provide additional security features (like rate limiting and request filtering).
- **Separation of Concerns**: Nginx separates concerns by handling HTTP-specific features, allowing the FastAPI application to focus on application logic.

Without Nginx, the FastAPI server would need to handle all incoming connections directly, which could limit scalability, security, and performance. Nginx provides a robust and efficient way to manage these aspects.
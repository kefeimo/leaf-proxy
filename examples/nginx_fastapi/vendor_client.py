import requests

url = "http://172.25.90.138/echo"

# Data to be sent in the POST request
data = "Hello, FastAPI via Nginx!"

response = requests.post(url, data=data, headers={"Content-Type": "text/plain"})

print(response.json())

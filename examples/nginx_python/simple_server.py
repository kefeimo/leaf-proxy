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

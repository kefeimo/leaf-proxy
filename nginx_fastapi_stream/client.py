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

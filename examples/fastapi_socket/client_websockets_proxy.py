import socket
import threading
from time import sleep

HOST = '0.0.0.0'
PORT = 80  # Starting port, make sure this matches the server's port

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
                    sleep(1)

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

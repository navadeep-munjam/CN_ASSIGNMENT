import socket
import threading

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8080

def receive_updates(client_socket):
    while True:
        try:
            update = client_socket.recv(1024).decode('utf-8')
            if update:
                print(f"Document updated: {update}")
        except ConnectionResetError:
            print("Connection to the server was lost.")
            break

def start_client():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print("Connected to the server. Start typing to edit the document:")

        # Start a thread to listen for updates from the server
        threading.Thread(target=receive_updates, args=(client_socket,), daemon=True).start()

        while True:
            user_input = input()
            client_socket.sendall(user_input.encode('utf-8'))

    except ConnectionError:
        print("Connection failed. Please check the server and try again.")
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()

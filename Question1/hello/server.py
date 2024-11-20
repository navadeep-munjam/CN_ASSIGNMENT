import socket
import threading
from threading import Lock

# Server settings
HOST = 'localhost'
PORT = 8080
MAX_CLIENTS = 10

# Shared document state and lock for synchronization
document = ""
clients = []
client_ids = {}
doc_lock = Lock()  # Mutex for document access
client_list_lock = Lock()  # Mutex for client list access

# Load or initialize `temp.txt`
try:
    with open("temp.txt", "r") as file:
        document = file.read()  # Load document state from file
except FileNotFoundError:
    print("temp.txt not found. Starting with an empty document.")
except Exception as e:
    print("Error opening file temp.txt:", e)

def broadcast(update, sender_socket=None):
    with client_list_lock:
        for client in clients:
            if client != sender_socket:
                try:
                    message = f"{len(update):<10}" + update  # Prefix with length header
                    client.sendall(message.encode())
                except Exception as e:
                    print("Error sending update:", e)

def handle_client(client_socket, client_address):
    global document

    # Assign a unique client ID and send the initial document state
    with client_list_lock:
        client_id = len(clients) + 1
        clients.append(client_socket)
        client_ids[client_socket] = client_id
        print(f"New client connected: {client_address} (ID: {client_id})")

    with doc_lock:
        client_socket.sendall(f"{len(document):<10}".encode() + document.encode())

    while True:
        try:
            # Read header to determine update length
            header = client_socket.recv(10)
            if not header:
                break
            update_length = int(header.decode().strip())
            update = client_socket.recv(update_length).decode()

            if not update:
                break

            # Critical section for updating document and writing to `temp.txt`
            with doc_lock:
                document += f"Client {client_id}: {update}\n"
                with open("temp.txt", "a") as file:
                    file.write(f"Client {client_id}: {update}\n")

            print(f"Received update from client {client_address} (ID: {client_id}): {update}")
            print("Broadcasting update to all clients")
            broadcast(f"Client {client_id}: {update}", client_socket)
        except Exception as e:
            print("Error with client communication:", e)
            break

    # Handle client disconnection
    with client_list_lock:
        clients.remove(client_socket)
        del client_ids[client_socket]
    client_socket.close()
    print(f"Client {client_address} (ID: {client_id}) disconnected")

def start_server():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(MAX_CLIENTS)
        print("Server listening on port 8080")
    except Exception as e:
        print("Server error: Unable to start server on port 8080:", e)
        return

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()

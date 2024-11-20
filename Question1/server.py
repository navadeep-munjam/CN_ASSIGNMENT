import socket
import threading

# Server Configuration
HOST = '127.0.0.1'
PORT = 8080
MAX_CLIENTS = 10
shared_document = ""
lock = threading.Lock()

def handle_client(client_socket, client_address):
    global shared_document
    print(f"New client connected: {client_address}")

    # Send the current document state to the client
    if shared_document:
        client_socket.sendall(shared_document.encode('utf-8'))

    try:
        while True:
            # Receive updates from the client
            update = client_socket.recv(1024).decode('utf-8')
            if not update:
                break

            # Append update to shared document
            with lock:
                shared_document += update + "\n"  # Ensure newline after each update
                with open("temp.txt", "a") as f:
                    f.write(update + "\n")  # Write update to file with newline

            print(f"Received update from client {client_address}: {update}")

            # Broadcast update to all connected clients except the sender
            for client in clients:
                if client != client_socket:
                    client.sendall(update.encode('utf-8'))
            
            print("Broadcasting update to all clients")
    except ConnectionResetError:
        print(f"Client {client_address} disconnected")
    finally:
        client_socket.close()
        with lock:
            clients.remove(client_socket)

def start_server():
    global shared_document
    # Load existing document content if available
    try:
        with open("temp.txt", "r") as f:
            shared_document = f.read()
    except FileNotFoundError:
        with open("temp.txt", "w") as f:
            pass  # Create the file if it doesn't exist

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(MAX_CLIENTS)
        print(f"Server listening on port {PORT}")

        while True:
            client_socket, client_address = server_socket.accept()
            clients.append(client_socket)
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()

    except socket.error:
        print("Server error: Unable to start server on port 8080")
    except IOError:
        print("Error opening file temp.txt")
    finally:
        server_socket.close()

if __name__ == "__main__":
    clients = []
    start_server()

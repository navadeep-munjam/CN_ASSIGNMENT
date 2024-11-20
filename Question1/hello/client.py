import socket
import threading

HOST = 'localhost'
PORT = 8080

def receive_updates(sock):
    while True:
        try:
            header = sock.recv(10)
            if not header:
                break
            update_length = int(header.decode().strip())
            update = sock.recv(update_length).decode()

            if not update:
                break

            print("Document updated:", update)
        except Exception as e:
            print("Error receiving updates:", e)
            break

def main():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        print("Connected to the server. Start typing to edit the document:")
    except Exception as e:
        print("Connection failed. Please check the server and try again.")
        return

    threading.Thread(target=receive_updates, args=(client_socket,)).start()

    while True:
        try:
            update = input()
            message = f"{len(update):<10}" + update
            client_socket.sendall(message.encode())
        except Exception as e:
            print("Error sending update:", e)
            break

    client_socket.close()

if __name__ == "__main__":
    main()

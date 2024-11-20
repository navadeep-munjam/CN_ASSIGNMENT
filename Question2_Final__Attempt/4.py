import socket
import threading
import os
from start_Server import start_node
class Node:
    def __init__(self, node_id, ip, port, peer_ips_ports):
        self.node_id = node_id
        self.ip = ip
        self.port = port
        self.peers = peer_ips_ports
        self.leader_id = None
        self.file_directory = os.getcwd() 
        self.peer_files = {}  
        self.server_socket = None
        self.is_running = True  
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)
        print(f"Node {self.node_id} listening on {self.ip}:{self.port}")



    def start_node(self):
        try:
            threading.Thread(target=self.listen_for_connections, daemon=True).start()
            threading.Thread(target=self.initiate_connections, daemon=True).start()

            while self.is_running:
                pass  

        except Exception as e:
            print(f"Error starting node {self.node_id}: {e}")

     #this code is used for listening of connections        

    def listen_for_connections(self):
        try:
            while self.is_running:
                conn, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_connection, args=(conn,)).start()
        except Exception as e:
            print(f"Error listening for connections on node {self.node_id}: {e}")

            #this one for handlingconnections

    def handle_connection(self, conn):
        try:
            data = conn.recv(1024).decode()
            print(f"Node {self.node_id} received data: {data}")  # Debugging line
            
            if data.startswith("ID"):
                try:
                    peer_id = int(data.split(":")[1])
                    print(f"Node {self.node_id} received ID from peer: {peer_id}")
                    self.evaluate_leader(peer_id)
                except ValueError as e:
                    print(f"Error parsing ID: {e}")

            elif data == "SEND":
                files = os.listdir(self.file_directory)
                conn.send(str(files).encode())

            elif data.startswith("REQ"):
                your_roollnumber_image = data.split(":")[1]
                self.handle_file_request(your_roollnumber_image, conn)

            elif data.startswith("FILE_REQUEST"):
                your_roollnumber_image = data.split(":")[1]
                self.handle_file_request_from_peer_x(your_roollnumber_image, conn)

        except Exception as e:
            print(f"Error handling connection: {e}")
        finally:
            conn.close()
#this is for to get image as input 
    def initiate_connections(self):
        for peer_ip, peer_port in self.peers:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((peer_ip, peer_port))
                client_socket.send(f"ID:{self.node_id}".encode())
                print(f"Node {self.node_id} sent ID:{self.node_id} to {peer_ip}:{peer_port}")

                your_roollnumber_image = "12241060.jpg" 
                client_socket.send(f"FILE_REQUEST:{your_roollnumber_image}".encode())
                print(f"Node {self.node_id} sent FILE_REQUEST:{your_roollnumber_image} to {peer_ip}:{peer_port}")

                response = client_socket.recv(1024).decode()
                if response == "404 Not Found":
                    print(f"File {your_roollnumber_image} not found in network.")
                else:
                    with open(your_roollnumber_image, "wb") as f:
                        while True:
                            data = client_socket.recv(1024)
                            if not data:
                                break
                            f.write(data)
                    print(f"File {your_roollnumber_image} received from peer.")
                client_socket.close()

            except Exception as e:
                print(f"Connection to peer {peer_ip}:{peer_port} failed - {e}")
# this is used to find leader using minumum  numneric number as leader from 1 2 3
    def evaluate_leader(self, peer_id):
        if self.leader_id is None or peer_id < self.node_id:
            self.leader_id = min(self.node_id, peer_id)

        if self.leader_id == self.node_id:
            print(f"Node {self.node_id} is the leader")
            self.collect_file_logs()

#to print thre log we use this below function
    def collect_file_logs(self):
        for peer_ip, peer_port in self.peers:
            try:
                inet=socket.AF_INET
                sockstream=socket.SOCK_STREAM
                client_socket = socket.socket(inet, sockstream)
                client_socket.connect((peer_ip, peer_port))
                client_socket.send("SEND".encode())
                file_log = client_socket.recv(1024).decode()
                print(f"Received file log from peer: {file_log}")
                
                peer_address = f"{peer_ip}:{peer_port}"
                self.peer_files[peer_address] = eval(file_log)
                
                client_socket.close()
                
                with open("peer_files.log", "a") as f:
                    f.write(f"Log from {peer_ip}:{peer_port}: {file_log}\n")

            except Exception as e:
                print(f"Failed to retrieve file log from {peer_ip}:{peer_port} - {e}")

    def handle_file_request(self, your_roollnumber_image, conn):
        if your_roollnumber_image in os.listdir(self.file_directory):
            with open(your_roollnumber_image, "rb") as f:
                conn.sendfile(f)
            print(f"Sent {your_roollnumber_image} to requester")
        else:
            file_location = self.find_file_in_peers(your_roollnumber_image)
            if file_location:
                peer_ip, peer_port = file_location.split(":")
                peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_socket.connect((peer_ip, int(peer_port)))
                peer_socket.send(f"REQ:{your_roollnumber_image}".encode())

                with open(your_roollnumber_image, "wb") as f:
                    while True:
                        data = peer_socket.recv(1024)
                        if not data:
                            break
                        f.write(data)

                peer_socket.close()
                print(f"File {your_roollnumber_image} received from peer and sent to requester")
                with open(your_roollnumber_image, "rb") as f:
                    conn.sendfile(f)
            else:
                conn.send("404 Not Found".encode())
                print(f"{your_roollnumber_image} not found in network")

    def handle_file_request_from_peer_x(self, your_roollnumber_image, conn):
        if your_roollnumber_image in os.listdir(self.file_directory):
            with open(your_roollnumber_image, "rb") as f:
                conn.sendfile(f)
            print(f"Sent {your_roollnumber_image} to Peer X")
        else:
            file_location = self.find_file_in_peers(your_roollnumber_image)
            if file_location:
                peer_ip, peer_port = file_location.split(":")
                peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_socket.connect((peer_ip, int(peer_port)))
                peer_socket.send(f"REQ:{your_roollnumber_image}".encode())

                with open(your_roollnumber_image, "wb") as f:
                    while True:
                        data = peer_socket.recv(1024)
                        if not data:
                            break
                        f.write(data)

                peer_socket.close()
                print(f"File {your_roollnumber_image} received from peer and sent to Peer X")
                with open(your_roollnumber_image, "rb") as f:
                    conn.sendfile(f)
            else:
                conn.send("404 Not Found".encode())
                print(f"File {your_roollnumber_image} not found in network")

    def find_file_in_peers(self, your_roollnumber_image):
        for peer, files in self.peer_files.items():
            if your_roollnumber_image in files:
                return peer
        return None

    def stop_node(self):
        self.is_running = False
        self.server_socket.close()
        print(f"Node {self.node_id} is shutting down.")

if __name__ == "__main__":
    node1 = Node(node_id=1, ip="127.0.0.1", port=5001, peer_ips_ports=[("127.0.0.1", 5002), ("127.0.0.1", 5003)])
    node2 = Node(node_id=2, ip="127.0.0.1", port=5002, peer_ips_ports=[("127.0.0.1", 5001), ("127.0.0.1", 5003)])
    node3 = Node(node_id=3, ip="127.0.0.1", port=5003, peer_ips_ports=[("127.0.0.1", 5001), ("127.0.0.1", 5002)])

    node1_thread = threading.Thread(target=node1.start_node)
    node2_thread = threading.Thread(target=node2.start_node)
    node3_thread = threading.Thread(target=node3.start_node)

    node1_thread.start()
    node2_thread.start()
    node3_thread.start()

    try:
        node1_thread.join()
        node2_thread.join()
        node3_thread.join()
    except KeyboardInterrupt:
        print("Program interrupted, stopping nodes...")
        node1.stop_node()
        node2.stop_node()
        node3.stop_node()

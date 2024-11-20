import socket
import threading
import os

def start_node(self):
    try:
        # Start listening for connections
        threading.Thread(target=self.listen_for_connections, daemon=True).start()
        # Start initiating connections to peers
        threading.Thread(target=self.initiate_connections, daemon=True).start()

        while self.is_running:
            pass  # Main thread can perform additional tasks or just wait

    except Exception as e:
        print(f"Error starting node {self.node_id}: {e}")
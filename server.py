import select
import socket
import types
import threading
from connection import Connection
from server_mem import Memory

class Server:
    """A generic IRC server."""

    def __init__(self):
        """Initialises a Server object."""
        self.memory = Memory()

    def start_server(self):
        """Starts the server."""
        self.memory.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Socket options
        self.memory.socket.bind((self.memory.ipv6_address, self.memory.port)) # Bind a socket to a given IP and port

        print(f"'{self.memory.server_name}' is now running on {self.memory.ipv6_address}:{self.memory.port}.")
    
    def event_loop(self):
        """Event loop for the server, listens for new connections and accepts them."""
        self.memory.socket.listen()

        while True:
            
            client_sckt, client_addr = self.memory.socket.accept() # Accept a connection from a new client and assigns them a unique socket

            conn = Connection(client_sckt, client_addr, self.memory)
            threading.Thread(target=conn.loop).start()


server = Server()
server.start_server()
server.event_loop()

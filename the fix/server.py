import select
import socket
import types
import threading
from connection import Connection

class Server:
    """A generic IRC server."""

    def __init__(self):
        """Initialises a Server object."""
        self.ipv4_address = "127.0.0.1"
        self.port = 6667

        self.server_name = "UoD_IRCServer"

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket_list = [self.socket] # A list of connected sockets.
        self.clients = {} # Stores client nicknames with their socket as a key.

        self.public_channels = {
            "#general" : [],
            "#other" : []
        }

    def start_server(self):
        """Starts the server."""
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Socket options
        self.socket.bind((self.ipv4_address, self.port)) # Bind a socket to a given IP and port

        print(f"'{self.server_name}' is now running on {self.ipv4_address}:{self.port}.")
    
    def event_loop(self):
        self.socket.listen()

        print("waiting....")
        read_sockets, _, exception_sockets = select.select(self.socket_list, [], self.socket_list) # Waits for new readable data from sockets
        print("eyy bois we got somthin")

        while True:
            for notif_socket in read_sockets: # Loop through sockets with new data to read
                if notif_socket == self.socket: # If the socket is the socket that this server runs on (new connection)
                    client_sckt, client_addr = self.socket.accept() # Accept a connection from a new client and assigns them a unique socket

                    conn = Connection(client_sckt, client_addr, self.clients, self.ipv4_address)
                    threading.Thread(target=conn.loop).start()


server = Server()
server.start_server()
server.event_loop()

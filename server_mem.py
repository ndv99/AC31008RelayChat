import socket

class Memory:
    """A class that stores data for the server that all the connection threads may need to access.
    """    

    def __init__(self):
        """Initialises the memory object.
        """        
        self.ipv4_address = "127.0.0.1"
        self.ipv6_address = "::1"
        self.port = 6667
        self.server_name = "my-awful-irc-server"
        self.server_version = "420.69"

        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.socket_list = [self.socket] # A list of connected sockets.
        self.clients = {} # Stores client nicknames with their socket as a key.

        self.channels = {
            "#general" : [],
            "#test" : []
        }
    

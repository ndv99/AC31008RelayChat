import socket

class Memory:
    """A class that stores data for the server that all the connection threads may need to access.
    """    

    def __init__(self, ipv6_addr):
        """Initialises the memory object.

        Args:
            ipv6_addr (string): A valid IPv6 address as a string
        """        
        self.ipv4_address = "127.0.0.1"
        self.ipv6_address = ipv6_addr
        self.port = 6667
        self.server_name = "my-awful-irc-server"
        self.server_version = "420.69"

        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.clients = {} # Stores client nicknames with their socket as a key.

        self.channels = {
            "#general" : [],
            "#test" : []
        }
    

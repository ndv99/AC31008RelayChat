import socket

class Memory:

    def __init__(self):
        self.ipv4_address = "127.0.0.1"
        self.port = 6667
        self.server_name = "UoD_IRCServer"

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_list = [self.socket] # A list of connected sockets.
        self.clients = {} # Stores client nicknames with their socket as a key.

        self.channels = {
            "#general" : [],
            "#test" : []
        }
    

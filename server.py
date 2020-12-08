import os
import socket
import select

class Server:

    def __init__(self):
        self.ipv4_address = "192.168.1.2"
        self.port = 6667
        self.command_prefix = "!"
        self.server_name = "UoD_IRCServer"

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ipv4_address, self.port))

        self.socket.listen()
        self.socket_list = [self.socket]
        self.clients = []
        self.channels = []

    def start_server(self):
        pass

    def receive(self):
        pass

    def send_to_server(self):
        pass

    def send_to_user(self):
        pass

    def create_channel(self):
        pass
    
server = Server()
server.start_server()

print("This is the server file.")
import socket

class Server:

    def __init__(self):
        self.ipv4_address = "127.0.0.1"
        self.port = 6667
        self.command_prefix = "!"
        self.server_name = "UoD_IRCServer"

    def start_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.bind((self.ipv4_address, self.port))
        self.socket.listen()
        
        self.socket_list = [self.socket]
        self.clients = []
        self.channels = []

        print(f"'{self.server_name}' is now running on {self.ipv4_address}:{self.port}")

    def receive(self):
        print("Waiting for client...")
        client_socket, client_address = self.socket.accept()
        self.socket_list.append(client_socket)
        print(f"Client {client_address} has joined the server!")

        with client_socket:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                client_socket.sendall(data)

    def send_to_server(self):
        pass

    def send_to_user(self):
        pass

    def create_channel(self):
        pass
    
server = Server()
server.start_server()
server.receive()

import selectors
import socket
import types

class Server:

    def __init__(self):
        self.ipv4_address = "127.0.0.1"
        self.port = 6667
        self.command_prefix = "!"
        self.server_name = "UoD_IRCServer"
        self.server_selector = selectors.DefaultSelector()

    def start_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.bind((self.ipv4_address, self.port))
        
        self.socket_list = [self.socket]
        self.clients = []
        self.channels = []

        print(f"'{self.server_name}' is now running on {self.ipv4_address}:{self.port}")

    def receive(self):
        self.socket.listen()
        print("Waiting for client...")

        self.socket.setblocking(False)
        self.server_selector.register(self.socket, selectors.EVENT_READ, data=None)

        while True:
            events = self.server_selector.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    self.accept_connection(key.fileobj)
                else:
                    self.service_connection(key, mask)

                # data = client_socket.recv(1024)
                # if not data:
                #     break
                # client_socket.sendall(data)
    
    def accept_connection(self, new_socket):
        client_socket, client_address = new_socket.accept()
        print(f"Accepted connection from {client_address}")
        client_socket.setblocking(False)
        self.socket_list.append(client_socket)

        data = types.SimpleNamespace(addr=client_address, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.server_selector.register(client_socket, events, data=data)
    
    def service_connection(self, key, mask):
        connection_socket = key.fileobj
        data = key.data

        if mask & selectors.EVENT_READ:
            data_received = connection_socket.recv(1024)  # Should be ready to read
            if data_received:
                data.outb += data_received
            else:
                print("Terminating connection to ", data.addr)
                self.server_selector.unregister(connection_socket)
                connection_socket.close()
                
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print("Echoing: ", repr(data.outb), " to ", data.addr)
                sent = connection_socket.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    def send_to_server(self):
        pass

    def send_to_user(self):
        pass

    def create_channel(self):
        pass
    
server = Server()
server.start_server()
server.receive()

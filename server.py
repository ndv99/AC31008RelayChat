import selectors
import socket
import types

class Server:
    """A generic IRC server."""

    def __init__(self):
        """Initialises a Server object."""
        self.ipv4_address = "127.0.0.1"
        self.port = 6667
        self.command_prefix = "!"
        self.server_name = "UoD_IRCServer"
        self.server_selector = selectors.DefaultSelector()

    def start_server(self):
        """Starts the server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.bind((self.ipv4_address, self.port))
        
        self.socket_list = [self.socket]
        self.clients = []
        self.channels = []

        print(f"'{self.server_name}' is now running on {self.ipv4_address}:{self.port}")

    def receive(self):
        """Waits to receive messages from clients."""
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
    
    def accept_connection(self, new_socket):
        """Accepst a connection from a client.
        
        Args:
            new_socket (SelectorKey.fileobj): The socket of the client to connect to.
        """
        client_socket, client_address = new_socket.accept()
        print(f"Accepted connection from {client_address}")
        client_socket.setblocking(False)
        self.socket_list.append(client_socket)

        data = types.SimpleNamespace(addr=client_address, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.server_selector.register(client_socket, events, data=data)
    
    def service_connection(self, key, mask):
        """Echoes a message back to a client.

        Args:
            key (SelectorKey): The selector key containing data for where to send data back to.
            mask (int): From DefaultSelector.select.
        """
        connection_socket = key.fileobj
        data = key.data

        if mask & selectors.EVENT_READ:
            data_received = connection_socket.recv(1024)
            if data_received:
                data.outb += data_received
            else:
                print("Terminating connection to ", data.addr)
                self.server_selector.unregister(connection_socket)
                connection_socket.close()
                
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print("Echoing: ", repr(data.outb), " to ", data.addr)
                sent = connection_socket.send(data.outb)
                data.outb = data.outb[sent:]

    def send_to_server(self):
        pass

    def send_to_user(self):
        pass

    def create_channel(self):
        pass
    
if __name__ == "__main__":
    server = Server()
    server.start_server()
    server.receive()

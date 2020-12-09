import select
import socket
import types

class Server:
    """A generic IRC server."""

    def __init__(self):
        """Initialises a Server object."""
        self.ipv4_address = "127.0.0.1"
        self.port = 6667

        self.command_prefix = "!"
        self.header_length = 10

        self.server_name = "UoD_IRCServer"

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket_list = [self.socket]
        self.clients = {}
        self.channels = []


    def start_server(self):
        """Starts the server."""
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ipv4_address, self.port))

        print(f"'{self.server_name}' is now running on {self.ipv4_address}:{self.port}.")

    def receive(self):
        """Waits to receive messages from clients."""
        self.socket.listen()
        print("Waiting for client...")

        while True:
            read_sockets, _, exception_sockets = select.select(self.socket_list, [], self.socket_list)

            for notif_socket in read_sockets:
                if notif_socket == self.socket:
                    client_sckt, client_addr = self.socket.accept()
                    user = self.receive_message(client_sckt)

                    if user is False:
                        continue

                    self.socket_list.appen(client_sckt)
                    self.clients[client_sckt] = user
                    print(f"{user['data'].decode('utf-8')} has connected to the server via {client_addr}")

                else:
                    msg = self.receive_message(notif_socket)
                    if msg is False:
                        print(f"Terminated connection with {self.clients[notif_socket]['data'].decode('utf-8')}")
                        self.socket_list.remove(notif_socket)
                        del self.clients[notif_socket]
                        continue
                    
                    user = self.clients[notif_socket]
                    username = user["data"].decode("utf-8")
                    message = msg["data"].decode("utf-8")
                    print(f"Received message from {username}: {message}")
                    self.send_to_server(user, msg, notif_socket)
        
        for notif_socket in exception_sockets:

            self.socket_list.remove(notif_socket)
            del self.clients[notif_socket]

    def receive_message(self, client_sckt):
        try:
            header = client_sckt.recv(self.header_length)
            if not len(header):
                return False
            
            message_length = int(header.decode('utf-8').strip())

            return header, client_sckt.recv(message_length)
        
        except:
            return False


    def send_to_server(self, user, msg, notif_socket):
        for client_sckt in self.clients:
            if client_sckt != notif_socket:
                client_sckt.send(user['header'] + user['data'] + msg['header'] + msg['data'])

    def send_to_user(self):
        pass

    def create_channel(self):
        pass
    
if __name__ == "__main__":
    server = Server()
    server.start_server()
    server.receive()

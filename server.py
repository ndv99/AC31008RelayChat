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

    def start_server(self):
        """Starts the server."""
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Socket options
        self.socket.bind((self.ipv4_address, self.port)) # Bind a socket to a given IP and port

        print(f"'{self.server_name}' is now running on {self.ipv4_address}:{self.port}.")

    def event_loop(self):
        """Main even loop for the program"""
        self.socket.listen() # Listen for messages from clients
        print("Waiting for client...")

        while True:
            read_sockets, _, exception_sockets = select.select(self.socket_list, [], self.socket_list) # Checks if any new data can be read from sockets

            for notif_socket in read_sockets: # If a sokcet has new data to read
                if notif_socket == self.socket:
                    client_sckt, client_addr = self.socket.accept() # Accept a connection from a new client
                    usr = self.receive_message(client_sckt) # Get user data from that client

                    if usr is False:
                        continue

                    self.socket_list.append(client_sckt) # Add client's socket to socket list
                    self.clients[client_sckt] = usr # Add client to client dictionary
                    username = usr['data'].decode('utf-8')
                    print(f"{username} has connected to the server.")

                else:
                    msg = self.receive_message(notif_socket) # Get message from socket
                    if msg is False: # Msg is false if client terminates connection
                        print(f"Terminated connection with {self.clients[notif_socket]['data'].decode('utf-8')}")
                        self.socket_list.remove(notif_socket) # Remove client's socket from socket list
                        del self.clients[notif_socket] # Delete client from client dictionary
                        continue # Skips the following code to send a message to all clients
                    
                    user = self.clients[notif_socket]
                    username = user['data'].decode("utf-8")
                    message = msg['data'].decode("utf-8")
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

            return {'header':header, 'data':client_sckt.recv(message_length)}
        
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
    server.event_loop()

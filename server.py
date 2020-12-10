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
            read_sockets, _, exception_sockets = select.select(self.socket_list, [], self.socket_list) # Waits for new readable data from sockets

            for notif_socket in read_sockets: # Loop through sockets with new data to read
                if notif_socket == self.socket: # If the socket is the socket that this server runs on (new connection)
                    client_sckt, client_addr = self.socket.accept() # Accept a connection from a new client and assigns them a unique socket
                    usr = self.receive_message(client_sckt) # Get user data from that client

                    if usr is False: # If client disconnected before sending name
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
                    
                    user = self.clients[notif_socket] # Get sender of the message
                    username = user['data'].decode("utf-8") # decode username
                    message = msg['data'].decode("utf-8") # decode message
                    print(f"Received message from {username}: {message}") # Output in server console
                    self.send_to_server(user, msg, notif_socket) # Send user's message to all other clients in the server
        
        for notif_socket in exception_sockets: # Removes any misbehaving sockets

            self.socket_list.remove(notif_socket)
            del self.clients[notif_socket]

    def receive_message(self, client_sckt):
        try:
            header = client_sckt.recv(self.header_length) # Receive message header - contains message length
            if not len(header): # Return false if there's no data received
                return False
            
            message_length = int(header.decode('utf-8').strip()) # convert header to int

            return {'header':header, 'data':client_sckt.recv(message_length)} # Return dictionary containing header and data
        
        except:
            return False


    def send_to_server(self, user, msg, notif_socket):
        for client_sckt in self.clients:
            if client_sckt != notif_socket:
                # Send username and message, as well as headers
                client_sckt.send(user['header'] + user['data'] + msg['header'] + msg['data'])

    def send_to_user(self):
        pass

    def create_channel(self):
        pass
    
if __name__ == "__main__":
    server = Server()
    server.start_server()
    server.event_loop()

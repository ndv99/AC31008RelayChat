import socket
import select
import errno

SERVER_HOSTNAME = "127.0.0.1"
SERVER_PORT = 6667

class Client:
    """A generic IRC client."""

    def __init__(self):
        """Initialises a Client object."""
        self.host_name = "127.0.0.1"
        self.port = 6667
        self.header_length = 10
        self.client_socket = None
        self.username = ""
        self.encoding_scheme = 'utf-8'

    def client_test_method(self):
        print("This is a test from the 'Client' class.")

    def connect_to_server(self, host, port):
        """Connects a Client to a server.
        
        Args:
            host (string): The hostname of the server as an IPv4 address (TO BE CHANGED TO IPV6).
            port (int): The port through which to connect to the server.
        """

        self.username = input("Enter a username: ")

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.client_socket.setblocking(False)

        username_encoded = self.username.encode(self.encoding_scheme)
        username_header = f"{len(self.username):<{self.header_length}}".encode(self.encoding_scheme)
        self.client_socket.send(username_header + username_encoded)

    def send_message(self):
        msg = input(f'{self.username} > ')

        if msg:
            msg = msg.encode(self.encoding_scheme)
            msg_header = f"{len(msg):<{self.header_length}}".encode(self.encoding_scheme)
            self.client_socket.send(msg_header + msg)

    def receive_messages(self):
        usr_header = self.client_socket.recv(self.header_length)

        if not len(usr_header):
            print("Server closed.")
            sys.exit()
        
        uname_length = int(usr_header.decode(self.encoding_scheme).strip())
        uname = self.client_socket.recv(uname_length).decode(self.encoding_scheme)

        msg_header = self.client_socket.recv(self.header_length)
        msg_length = int(msg_header.decode(self.encoding_scheme).strip())
        msg = self.client_socket.recv(msg_length).decode(self.encoding_scheme)

        print(f"{uname}: {msg}")

    def event_loop(self):
        while True:
            self.send_message()
            
            try:
                while True:
                    self.receive_messages()
            except IOError as io_error:
                if io_error.errno != errno.EAGAIN and io_error.errno != errno.EWOULDBLOCK:
                    print(f"Reading error: {str(io_error)}")
                    sys.exit()
                
                continue
            except Exception as exception:
                print(f"Reading error: {str(io_error)}")
                sys.exit()

    def join_channel(self):
        pass

if __name__ == "__main__":
    client = Client()
    client.connect_to_server(SERVER_HOSTNAME, SERVER_PORT)
    client.event_loop()

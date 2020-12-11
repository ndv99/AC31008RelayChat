import threading
import select
import socket
import errno

SERVER_HOSTNAME = "127.0.0.1"
SERVER_PORT = 6667

class Client:
    """A generic IRC client."""

    def __init__(self):
        """Initialises a Client object."""
        self.host_name = "127.0.0.1"
        self.port = 6667
        self.header_length = 1024
        self.client_socket = None
        self.username = ""
        self.encoding_scheme = 'utf-8'
        self.server_name = ""

        self.message_colours = {
            'default': "\033[0;37;40m",
            'server': "\033[0;34;40m",
            'error': "\033[0;31;40m",
            'client': "\033[0;32;40m",
            'bot': "\033[0;33;40m"
        }

    def connect_to_server(self, host, port):
        """Connects a Client to a server.
        
        Args:
            host (string): The hostname of the server as an IPv4 address (TO BE CHANGED TO IPV6).
            port (int): The port through which to connect to the server.
        """
        valid_username = False

        while not valid_username:
            self.username = input("Enter a username: ")

            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            self.client_socket.setblocking(False)

            username_encoded = self.username.encode(self.encoding_scheme)
            username_header = f"{len(self.username):<{self.header_length}}".encode(self.encoding_scheme)
            self.client_socket.send(username_header + username_encoded)

            read_sockets, _, exception_sockets = select.select([self.client_socket], [], [self.client_socket]) # Waits for new readable data from sockets

            for notif_socket in read_sockets: # Loop through sockets with new data to read
                if notif_socket == self.client_socket:
                    uname, msg = self.receive_messages(show=False)
                    self.server_name = uname
                    if msg == "conn_accepted":
                        valid_username = True
                        self.display_message(uname, f"Welcome to {uname}! Type '$help' to get help with commands.")
                    else:
                        self.display_message(uname, f"Username '{self.username}' is already taken. Try another name.", msg_type="error")
        
    
    def display_message(self, usr, msg, msg_type=None):
        if msg_type is None:
            user_types = {
                self.username: "default",
                self.server_name: "server",
                f"{self.server_name}_error": "error",
                "IRCBot": "bot"
            }
            if usr not in user_types:
                msg_type = "client"
            else:
                msg_type = user_types[usr]
        print(f"{self.message_colours[msg_type]} {usr}: {msg} \033[0;37;40m")
                        

    def send_message(self):
        while True:
            msg = input('')

            if msg:
                msg = msg.encode(self.encoding_scheme)
                msg_header = f"{len(msg):<{self.header_length}}".encode(self.encoding_scheme)
                self.client_socket.send(msg_header + msg)

    def receive_messages(self, show=True):
        usr_header = self.client_socket.recv(self.header_length)

        if not len(usr_header):
            print("Server closed.")
            exit()
        
        uname_length = int(usr_header.decode(self.encoding_scheme).strip())
        uname = self.client_socket.recv(uname_length).decode(self.encoding_scheme)

        msg_header = self.client_socket.recv(self.header_length)
        msg_length = int(msg_header.decode(self.encoding_scheme).strip())
        msg = self.client_socket.recv(msg_length).decode(self.encoding_scheme)

        if show:
            self.display_message(uname, msg)
        
        return uname, msg

    def event_loop(self):
        send_thread = threading.Thread(target=self.send_message)
        send_thread.daemon = True
        send_thread.start()
        while True:
            try:
                while True:
                    self.receive_messages()
            except IOError as io_error:
                if io_error.errno != errno.EAGAIN and io_error.errno != errno.EWOULDBLOCK:
                    print(f"Reading error: {str(io_error)}")
                    exit()
                
                continue
            except Exception as exception:
                print(f"Reading error: {str(io_error)}")
                exit()

    def join_channel(self):
        pass

if __name__ == "__main__":
    client = Client()
    client.connect_to_server(SERVER_HOSTNAME, SERVER_PORT)
    client.event_loop()

import socket

SERVER_HOSTNAME = "127.0.0.1"
SERVER_PORT = 6667

class Client:

    def __init__(self):
        self.host_name = "127.0.0.1"
        self.port = 6667
        self.client_socket = None

    def client_test_method(self):
        print("This is a test from the 'Client' class.")

    def connect_to_server(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.client_socket.sendall(b'fucking hate this shite fam')
        data = self.client_socket.recv(1024)

        print(f"Received: {repr(data)}")

    def send_message(self):
        pass

    def join_channel(self):
        pass

client = Client()
client.connect_to_server(SERVER_HOSTNAME, SERVER_PORT)
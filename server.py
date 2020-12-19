import select
import socket
import types

class Server:
    """A generic IRC server."""

    def __init__(self):
        """Initialises a Server object."""
        self.ipv4_address = "127.0.0.1"
        self.port = 6667

        self.command_prefix = "$"
        self.header_length = 512
        # self.commands = [
        #     "$help: Shows all commands",
        #     "$join <channel>: Moves you to <channel>",
        #     "$private <user>: Begins private messaging with <user>",
        #     "$channels: Displays a list of channels in the server"]

        self.commands = ["JOIN", "PRIVMSG", "NAMES"]

        self.server_name = "UoD_IRCServer"
        self.server_name_error = f"{self.server_name}_error"
        self.server_metadata = {
            'header': f"{len(self.server_name):<{self.header_length}}".encode('utf-8'),
            'data': self.server_name.encode('utf-8')
            }

        self.error_message_metadata = {
            'header': f"{len(self.server_name_error):<{self.header_length}}".encode('utf-8'),
            'data': self.server_name_error.encode('utf-8')
            }

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket_list = [self.socket] # A list of connected sockets.
        self.clients = {} # Stores client nicknames with their socket as a key.
        self.public_channels = {
            "#general" : [],
            "#other" : []
        }
        self.private_channels = {

        }

    def start_server(self):
        """Starts the server."""
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Socket options
        self.socket.bind((self.ipv4_address, self.port)) # Bind a socket to a given IP and port
        self.socket.settimeout(5)

        print(f"'{self.server_name}' is now running on {self.ipv4_address}:{self.port}.")

    def handle_command(self, message, notif_socket):
        message = message.split(" ")
        if message[0] == "JOIN":
            if len(message) > 1:
                print(message[1])
                if message[1].lower() not in self.public_channels:
                    msg_content = f"ERR_NOSUCHCHANNEL"
                    self.send_code(msg_content, notif_socket)
                else:
                    self.remove_client_from_channel(notif_socket)
                    self.assign_client_channel(message[1].lower(), notif_socket)
        elif message[0] == "NAMES":
            channels = []
            for channel in self.public_channels:
                channels.append(channel)
            msg_content = f"Channels: {channels}"
            msg = self.compose_message(msg_content)
            self.send_to_user(self.server_metadata, msg, notif_socket)
        # elif message[0] == "$help":
        #     for command in self.commands:
        #         msg_content = f"{command}"
        #         msg = self.compose_message(msg_content)
        #         self.send_to_user(self.server_metadata, msg, notif_socket)
        elif message[0] == "PRIVMSG":
            if len(message) > 1:
                uname_list = []
                for client in self.clients:
                    uname_list.append(self.get_username(client))
                if message[1] != self.get_username(notif_socket):
                    if message[1] not in uname_list:
                        msg_content = f"'{message[1]}' is not a valid username. Use $users to get a list of usernames."
                        msg = self.compose_message(msg_content)
                        self.send_to_user(self.error_message_metadata, msg, notif_socket)
                    else:
                        notif_uname = self.get_username(notif_socket)
                        recip_socket = None
                        for client in self.clients:
                            if self.get_username(client) == message[1]:
                                recip_socket = client
                                break
                        self.private_channels[f'{notif_uname}|{message[1]}'] = [notif_socket, recip_socket]
                        self.remove_client_from_channel(notif_socket)
                        self.remove_client_from_channel(recip_socket)

                        msg_content = f"You are now in a private channel with {message[1]}"
                        msg = self.compose_message(msg_content)
                        self.send_to_user(self.server_metadata, msg, notif_socket)

                        msg_content = f"You are now in a private channel with {notif_uname}"
                        msg = self.compose_message(msg_content)
                        self.send_to_user(self.server_metadata, msg, recip_socket)
        else:
            msg_content = f"'{message[0]}' is not a valid command. Use $help to get a list of commands."
            msg = self.compose_message(msg_content)
            self.send_to_user(self.error_message_metadata, msg, notif_socket)

    def event_loop(self):
        """Main event loop for the program"""
        self.socket.listen() # Listen for messages from clients
        print("Waiting for client...")

        while True:
            print("waiting....")
            read_sockets, _, exception_sockets = select.select(self.socket_list, [], self.socket_list) # Waits for new readable data from sockets
            print("eyy bois we got somthin")
            for notif_socket in read_sockets: # Loop through sockets with new data to read
                if notif_socket == self.socket: # If the socket is the socket that this server runs on (new connection)
                    client_sckt, client_addr = self.socket.accept() # Accept a connection from a new client and assigns them a unique socket
                    
                    # https://ircv3.net/specs/core/capability-negotiation.htmls

                    nickname = self.handshake(client_sckt)
                    if nickname:
                        print("received a new nickname")
                        success = self.hold_new_client(client_sckt, nickname)
                        if success:
                            print("we did it bois")
                        else:
                            print("nope")
                    else:
                        continue

                else:
                    msg = self.receive_message(notif_socket) # Get message from socket
                    if msg is False: # Msg is false if client terminates connection
                        print(f"Terminated connection with {self.clients[notif_socket]}")
                        self.remove_client_from_channel(notif_socket)
                        self.socket_list.remove(notif_socket) # Remove client's socket from socket list
                        del self.clients[notif_socket] # Delete client from client dictionary
                        continue # Skips the following code to send a message to all clients
                    
                    user = self.clients[notif_socket] # Get sender of the message
                    message = msg.decode("utf-8")[:-2] # decode message
                    print(f"Received message from {user}: {message}") # Output in server console

                    if message.split(" ")[0] in self.commands:
                        print("Message is command.")
                        self.handle_command(message, notif_socket)
                    else:
                        self.send_to_channel(user, msg, notif_socket) # Send user's message to all other clients in the channel
        
        for notif_socket in exception_sockets: # Removes any misbehaving sockets

            self.socket_list.remove(notif_socket)
            del self.clients[notif_socket]
    
    def handshake(self, client_sckt):
        print("We made it here")
        handshake = []
        for i in range(2):
            msg = self.receive_message(client_sckt) # Get user data from that client
            print(msg)
            if msg:
                msg = msg.decode('utf-8')[:-2].split('\r\n')
                for part in msg:
                    handshake.append(part)
            else:
                return False

        nickname = handshake[1].split(" ")[1]
        return nickname
    
    def hold_new_client(self, client_sckt, usr): # Checks against username rules in IRC spec
        if len(usr) > 9 or usr[0] == "-":
            print("Client tried to connect with invalid username")
            code = "432"
            msg = f"Nickname '{usr}' is invalid."
            self.send_code(code, client_sckt, msg, usr)
            return False
        
        try:
            if int(usr[0]):
                print("Client tried to connect with invalid username")
                msg = "ERR_NONICKNAMEGIVEN"
                self.send_to_user(self.server_metadata, msg, client_sckt)
                return False
        except ValueError:
            pass
        
        for client in self.clients:
            if self.clients[client].decode('utf-8') == usr:
                print("Client tried to connect with invalid username")
                msg = "ERR_NICKCOLLISION"
                self.send_to_user(self.server_metadata, msg, client_sckt)
                return False


        self.socket_list.append(client_sckt) # Add client's socket to socket list
        self.clients[client_sckt] = usr # Add client to client dictionary

        msg = f"Welcome to the Internet Relay Network, {usr}."
        self.send_to_server(self.server_name, msg, client_sckt)
        print(f"New client {usr} has connected.")
        # self.assign_client_channel('#general', client_sckt)
        return True
    
    def compose_message(self, content):
        msg_content = content.encode('utf-8')
        msg_header = f"{len(content):<{self.header_length}}".encode('utf-8')

        msg = {
            'header': msg_header,
            'data': msg_content
        }

        return msg
        
    def assign_client_channel(self, channel_name, client_sckt):
        users_in_channel = []
        for sckt in self.public_channels[channel_name]:
            uname = self.clients[sckt]['data'].decode('utf-8')
            users_in_channel.append(uname)

        self.public_channels[channel_name].append(client_sckt)
        msg_content = "JOIN"
        self.send_code(msg_content, client_sckt)
        msg_content = f"RPL_TOPIC none"
        self.send_code(msg_content, client_sckt)
        msg_content = f"RPL_NAMREPLY {self.get_channel_usernames(channel_name)}"
        self.send_code(msg_content, client_sckt)
        
        # msg_content = f"{self.get_username(client_sckt)} has joined {channel_name}"
        # self.send_to_channel(self.server_name, msg, client_sckt)

    def remove_client_from_channel(self, notif_socket):
        priv_channel = True
        try:
            for channel in self.public_channels:
                if notif_socket in self.public_channels[channel]:
                    priv_channel = False
                    msg_content = f"{self.get_username(notif_socket)} has left {channel}"
                    msg = self.compose_message(msg_content)
                    self.send_to_channel(self.server_metadata, msg, notif_socket)
                    self.public_channels[channel].remove(notif_socket)
        except KeyError:
            pass
        
        try:
            if priv_channel:
                clients = []
                private_channel = None
                for channel in self.private_channels:
                    if notif_socket in self.private_channels[channel]:
                        private_channel = channel
                        for client_socket in self.private_channels[channel]:
                            clients.append(client_socket)
                
                for client_socket in clients:
                    if client_socket != notif_socket:
                        self.assign_client_channel('general', client_socket)
                    self.private_channels[private_channel].remove(client_socket)
                del self.private_channels[private_channel]
        except KeyError:
            pass

    def get_username(self, client_sckt):
        return self.clients[client_sckt]

    def get_channel_usernames(self, channel_name):
        names = []
        for sckt in self.public_channels[channel_name]:
            names.append(self.clients[sckt])
        
        return names

    def receive_message(self, client_sckt):
        try:
            msg = client_sckt.recv(4096) # Receive message
            if not len(msg): # Return false if there's no data received
                return False

            return msg
        
        except Exception as e:
            print(e)
            return False

    def send_to_server(self, author, msg, notif_socket):
        for client_sckt in self.clients:
            client_sckt.send(f"{author}: {msg}\r\n".encode('utf-8'))
    
    def send_to_channel(self, author, msg, notif_socket):
        # find client's channel
        public_msg = False
        for channel in self.public_channels:
            if notif_socket in self.public_channels[channel]:
                for client_sckt in self.public_channels[channel]:
                    if client_sckt != notif_socket:
                        # Send username and message, as well as headers
                        client_sckt.send(author['header'] + author['data'] + msg['header'] + msg['data'])
                        public_msg = True
        
        if public_msg == False:
            for channel in self.private_channels:
                if notif_socket in self.private_channels[channel]:
                    for client_sckt in self.private_channels[channel]:
                        if client_sckt != notif_socket:
                            # Send username and message, as well as headers
                            client_sckt.send(author['header'] + author['data'] + msg['header'] + msg['data'])

    def send_to_user(self, author, msg, client_sckt):
        client_sckt.send(f"{author}: {msg}\r\n".encode('utf-8'))
    
    def send_code(self, code, client_sckt, msg, usr):
        client_sckt.send(f":{self.ipv4_address} {code} * {usr} :{msg}\r\n".encode('utf-8'))
    
if __name__ == "__main__":
    server = Server()
    server.start_server()
    server.event_loop()

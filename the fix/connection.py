class Connection:

    def __init__(self, sckt, addr, conns, ip):
        self.socket = sckt
        self.address = addr
        self.nickname = ""
        self.realname = ""
        self.ip = ip
        self.nick_set = False

        self.connections = conns
        self.commands = [
            "CAP",
            "NICK",
            "USER"
        ]

    def loop(self):
        try:
            while True:
                msg = self.socket.recv(4096)
                print(msg)
                msg = msg.decode().split('\r\n')[:-2]

                for part in msg:
                    print(part)
                    self.check_command(part)
        except ConnectionResetError:
            print("connection reset")
        except BrokenPipeError:
            print("Broken pipe")
    
    def check_command(self, cmd):
        cmd = cmd.split(" ")
        if cmd[0] in self.commands:
            if cmd[0] == "NICK":
                self.set_nickname(cmd[1])
    
    def set_nickname(self, nickname):
        if len(nickname) > 9 or nickname[0] == "-":
            print("Client tried to connect with invalid username")
            code = "432"
            msg = f"'{nickname}' is invalid."
            self.send_code(code, self.socket, msg, nickname)
            return False
        
        try:
            if int(nickname[0]):
                print("Client tried to connect with invalid username")
                code = "432"
                msg = f"'{nickname}' is invalid."
                self.send_code(code, client_sckt, msg, nickname)
                return False
        except ValueError:
            pass
        
        for client in self.connections:
            if self.connections[client].decode('utf-8') == nickname:
                print("Client tried to connect with taken username")
                code = "436"
                msg = f"'{nickname}' is already taken."
                self.send_code(code, client_sckt, msg, nickname)
                return False
        
        if not self.set_nickname:
            msg = f"NICK {nickname}"
            self.send_message(self.socket, msg)
            self.set_nickname = True
        else:
            msg = ""

    def send_code(self, code, sckt, usr, msg):
        sckt.send(f":{self.ip} {code} * {usr} :{msg}\r\n".encode())
    
    def send_message(self, sckt, msg):
        sckt.send(f":{self.ip} {msg}\r\n".encode())
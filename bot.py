import socket
import random
import sys
import string
import client

class Bot(client.Client):
    """An implementation of Client as a bot to perform commands from users at runtime."""

    def __init__(self):
        pass

    def listen(self):
        pass

    def check_for_command(self):
        pass

    def reply(self):
        pass

    def parse_server_data(self):
        pass
    
    def bot_test_method(self):
        print("This is a test from the 'Bot' class.")

print("This is the bot file.")

if __name__ == "__main__":
    bot = Bot()
    bot.client_test_method()
    bot.bot_test_method()
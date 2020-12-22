# AC31008RelayChat
The code for the final networks assignment - a basic client and a simplified server for real-time group talk (Internet Relay Chat).

## Getting started
1. Make sure you've downloaded Python 3.9
2. Create a virtual environment on this folder with `py -m venv AC31008RelayChat`
3. Enter the virtual environment using the `activate` script in \Scripts: `Scripts\activate`
4. Use `pip` to install the bot's requirements: `pip install -r requirements.txt`

## Running the server
1. In your terminal, run the server as follows: `py server.py`
    - In order to expose this server to other devices on your network, you'll need to provide an IPv6 address as an argument. Example:
    `py server.py 2a02:c7f:145d:4600:3050:a573:f51d:f954`
2. The server should now be up and running (on localhost by default). To connect, open your favourite IRC client and add the server, giving either the IP address you assigned it or localhost, followed by the port 6667. Examples:
    - localhost/6667
    - 2a02:c7f:145d:4600:3050:a573:f51d:f954/6667

3. Enter a username (9 characters maximum) and connect to the server!

## Running the bot
1. In your terminal, run the bot as follows: py bot.py
    - To connect the bot to a server running on another computer, you'll need to provide its IPv6 address as an argument. Example: `py bot.py 2a02:c7f:145d:4600:3050:a573:f51d:f954`
2. The bot should now be up and running, and it should be in every channel on the server.

## Using the bot

The bot only has three commands:
- `!hello` - Greets the user by their nickname and sends them the date and time
- `!slap` - Slaps a random user with a trout (in the face!)
- The bot will respond to private messages with a randomly chosen pun. This may or may not be a computing-related pun.

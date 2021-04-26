# VideoCallApp

A server and client app that allows multiple clients to connect to a server simultaneously and send messages/ files between one another. 

# Running the app

To run the app:

1. python3 server.py [maximum attempts allowed at login] [server port]

Run clients in separate folders:

1. python3 client.py [server address] [server port] [client UDP port for file sharing]


# Connection types

Clients send files to one another via UDP.
Clients interact with server via TCP

# Languages

- Python

# Description

VideoCallApp is a multi-threaded python app that allows for the sharing of files between users as well as the sending of messages.

Users are able to:
- Send messages
- Read messages sent by other users
- View active users
- Delete messages
- Edit messages
- Log in to their account
- Log out of their acocunt
- Send files to another user
- Receive files from another user


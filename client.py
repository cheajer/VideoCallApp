import socket
import threading
import time
import datetime as dt
import sys
from client_helpers import *

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverAddr = sys.argv[1]
serverPort = int(sys.argv[2])
# clientPort = int(sys.argv[3])
loggedIn = False

print('Waiting for connection')
try:
    clientSocket.connect((serverAddr, serverPort))
    print("successful connection")
except socket.error as e:
    print(str(e))

while True:
    if loggedIn == False:
        username = input("Username: ")
        password = input("Password: ")
        message = username + " " + password
        clientSocket.send(str.encode(message))
        receivedMessage = clientSocket.recvfrom(1024)
        receivedMessage=receivedMessage[0]
        if (receivedMessage.decode()=='Login Successful'):
            print(receivedMessage.decode())
            loggedIn=True
        elif receivedMessage.decode() == 'Login Attempt Limit Reached. Try again in 10 seconds.':
            print(receivedMessage.decode())
        else:
            print(receivedMessage.decode())
    else:
        command = input(printCommands())
        if checkValidCommand(command):
            clientSocket.send(str.encode(command))
        else:
            print("Invalid Command.")

clientSocket.close()
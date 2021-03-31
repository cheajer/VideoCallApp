from socket import *
import threading
import time
import datetime as dt
import sys
from client_helpers import *

# serverIP = sys.argv[1]
# serverPort = sys.argv[2]
# serverUDPPort = sys.argv[3]

#Server would be running on the same host as Client
serverName = sys.argv[1]
serverPort = int(sys.argv[2])

clientSocket = socket(AF_INET, SOCK_DGRAM)

while (1):
    username = input("Username: ")
    password = input("Password: ")
    message = username + " " + password
    clientSocket.sendto(message.encode(),(serverName, serverPort))
    #wait for the reply from the server
    receivedMessage, serverAddress = clientSocket.recvfrom(2048)

    if (receivedMessage.decode()=='Login Successful'):
        print(receivedMessage.decode())
        command = input(printCommands())
        clientSocket.sendto(command.encode(),(serverName, serverPort))

        #Wait for 10 back to back messages from server
        while 1:
            receivedMessage, serverAddress = clientSocket.recvfrom(2048)
            print(receivedMessage.decode())
        break
    elif receivedMessage.decode() == 'Login Attempt Limit Reached. Try again in 10 seconds.':
        print(receivedMessage.decode())
    else:
        print(receivedMessage.decode())

clientSocket.sendto(message.encode(),(serverName, serverPort))
clientSocket.close()
# Close the socket
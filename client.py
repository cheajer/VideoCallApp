import socket
import threading
import time
import datetime as dt
from _thread import *
import sys
from client_helpers import *
import json
import os

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverAddr = sys.argv[1]
serverPort = int(sys.argv[2])
active_users = []
clientPort = int(sys.argv[3])
loggedIn = False
UDPclientSocket = False

 
def UDP_threaded_client(clientPort):
    '''
    Creates and binds a new UDP socket to client specified port.
    Listens for incoming packets from other clients.

    clientPort - client port to bind UDP socket to.  
    '''
    global UDPclientSocket
    UDPclientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPclientSocket.bind(('localhost', clientPort))

    # Listens for files sent by other clients
    while True:
        data, addr = UDPclientSocket.recvfrom(1024)
        filename = data.decode()
        f=open(filename, 'wb')
        print(f'\n{filename} is being sent to you.')
        data, addr = UDPclientSocket.recvfrom(2048)
        fileLength = int(data.decode())
        byteCount = 0
        # Continue until EOF
        while byteCount <= fileLength:
            print(f'Downloading {filename}...')
            data, address = UDPclientSocket.recvfrom(2048)
            f.write(data)
            byteCount= byteCount+2048
        print(f'{filename} has been downloaded.')
        print(printCommands())
        f.close()


print('Waiting for connection')
try:
    clientSocket.connect((serverAddr, serverPort))
    print("successful connection")
except socket.error as e:
    print(str(e))


while True:
    # If loggedIn flag is false, asks user for 'username', and 'password' to attempt authentication
    if loggedIn == False:
        username= None
        password= None
        while username is None or username == "":
            username = input("Username: ")
        while password is None or password == "":
            password = input("Password: ")
        message = username + " " + password+" "+ str(clientPort)
        clientSocket.send(str.encode(message))
        receivedMessage = clientSocket.recvfrom(1024)
        receivedMessage=receivedMessage[0]
        # If server notifies of successful authentication, create a new UDP thread and set loggedIn to true
        if (receivedMessage.decode()=='Login Successful'):
            print(receivedMessage.decode())
            start_new_thread(UDP_threaded_client, (clientPort,))
            loggedIn=True
        # If server notifies that user has made too many incorrect attempts, print message
        elif receivedMessage.decode() == 'Login Attempt Limit Reached. Try again in 10 seconds.':
            print(receivedMessage.decode())
        # Otherwise, the user has inputted incorrect details (username not matching any in credentials.txt)
        else:
            print(receivedMessage.decode())
    # If loggedIn == True, ask user for commands
    else:
        command = input(printCommands())
        confirmation = 'A' # a flag used for confirmation of OUT and EDT functions
        # Check if the command entered is valid and exists, otherwise ask for a new command.
        if checkValidCommand(command):
            clientSocket.send(str.encode(command))
            receivedMessage = clientSocket.recvfrom(1024)
            receivedMessage=receivedMessage[0]
            # Active User Function
            if command == 'ATU':
                active_users = receivedMessage.decode().split('\n')
            # Upload Function
            elif command.split(' ')[0] == 'UPD':
                try:
                    port=getPortbyUsername(active_users, command.split(' ')[1]) # Get port of username specified by current user
                    try:
                        f = open(command.split(' ')[2], 'rb') # Open file specified by user
                    except:
                        print("Invalid Filename")
                        continue
                    UDPclientSocket.sendto(str.encode(username+'_'+command.split(' ')[2]), ('localhost', int(port))) # Send destination filename (i.e. username_example.txt)
                    UDPclientSocket.sendto(str.encode(str(os.path.getsize(command.split(' ')[2]))), ('localhost', int(port))) # Send file size so that receiver can process
                    fileBuffer = f.read(2048)
                    # Loop through the entire file until EOF
                    while fileBuffer:
                        UDPclientSocket.sendto(fileBuffer, ('localhost', int(port)))
                        print("Uploading..")
                        fileBuffer=f.read(2048)
                    f.close()
                    receivedMessage = f'File sent to client port no. {port}' # Print success message!
                    receivedMessage = receivedMessage.encode()
                except:
                    print("User not online")
            # OUT Function
            elif receivedMessage.decode()=='Logout request':
                while confirmation != "Y" and confirmation != "N": #Ask for confirmation from user
                    confirmation=input("Are you sure you want to logout (Y/N)?\n")
                clientSocket.send(str.encode(confirmation)) 
                receivedMessage = clientSocket.recvfrom(1024)
                receivedMessage=receivedMessage[0]
                if receivedMessage.decode() == "Thank you for using our service. Goodbye.": 
                    print(receivedMessage.decode())
                    clientSocket.close()
                    sys.exit()
            # EDT Function
            elif receivedMessage.decode()=='Edit request':
                while confirmation != "Y" and confirmation != "N": # Ask for confirmation from user
                    confirmation=input("Are you sure you want to edit this message (Y/N)?\n")
                clientSocket.send(str.encode(confirmation))
                receivedMessage = clientSocket.recvfrom(1024)
                receivedMessage=receivedMessage[0]
            print(receivedMessage.decode())
        else:
            print("Invalid Command.")


# If while loop is exited, close socket and end program.
clientSocket.close()


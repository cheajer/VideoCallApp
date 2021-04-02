import socket
import os
from _thread import *
import threading
import time
import datetime as dt
import sys
from server_helpers import *

def timeoutHandler(username):
    global clients
    for user in clients:
        if user['username'] == username:
            user['attemptNo']=0
    print("User may now attempt to login again.")
    

serverPort = int(sys.argv[2])
attemptsAllowed = int(sys.argv[1])

if len(sys.argv) < 3:
    print("Invalid number of arguments.")

if attemptsAllowed not in range(1,5):
    print(f"Invalid number of allowed failed consecutive attempt: {attemptsAllowed}. The valid value of argument number is an integer between 1 and 5") 
    sys.exit()

t_lock=threading.Condition()

#will store clients info in this list
clients=[]
#will store messages
messages=[]
# would communicate with clients after every second
UPDATE_INTERVAL= 1
timeout=False
clients = createClientList()

ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '0.0.0.0'
port = serverPort
ThreadCount = 0
open('userlog.txt', 'w').close()
open('messagelog.txt', 'w').close()
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waiting for a Connection..')
ServerSocket.listen(20)


def threaded_client(connection, clientAddress):
    global t_lock
    global serverSocket
    global clients
    global messages

    while True:
        data = connection.recv(2048)
        message = data.decode().split()
        print(checkUserStatus(clientAddress, clients))
        with t_lock:
            print(clients)
            if checkUserStatus(clientAddress, clients) == False:      #if user is not logged in or not a valid username
                username, password=message
                validUserAttempts = 0
                authFlag = CheckLoginDetails(username, password) # valid credentials or not

                clients, validUserAttempts=IncrementAttemptNo(username, clients) # increments attempt count for valid username input
                checkUserStatus(username, clients)

                if validUserAttempts == attemptsAllowed and authFlag == False:
                    t=threading.Timer(10, timeoutHandler, args=(username,))
                    serverMessage="Login Attempt Limit Reached. Try again in 10 seconds."
                    t.start()
                elif validUserAttempts > attemptsAllowed:
                    serverMessage="Login Attempt Limit Reached. Try again in 10 seconds."

                else:
                    currtime = dt.datetime.now()
                    date_time = currtime.strftime("%d/%m/%Y, %H:%M:%S")                

                    if authFlag == True:
                        serverMessage="Login Successful"
                        clients=logUserIn(username,clients, clientAddress)
                        userlog = f'{getActiveUsers(clients)}; {date_time}; {username}; {clientAddress[0]}; {clientAddress[1]}'
                        f=open("userlog.txt", "a")
                        print(userlog)
                        print(userlog, file=f)              
                        f.close()
                    else:
                        serverMessage="Login Unsuccessful. Try again."
            else: #if user is already logged in
                command = message[0]
                if command == "MSG":
                    print("MSG Function")
                    newMSG=newMessage(message, getUsername(clientAddress, clients), len(messages)+1)
                    messages.append(newMSG)
                    messageNumber=newMSG['messageNumber']
                    timestamp=newMSG['timestamp']
                    usernameMSG=newMSG['username']
                    messageBody=newMSG['message']
                    edited=newMSG['edited']
                    messagelog=f'{messageNumber}; {timestamp}; {usernameMSG}; {messageBody}; {edited}'
                    f=open("messagelog.txt", "a")
                    print(messagelog)
                    print(messagelog, file=f)
                    f.close()

                elif command == "DLT":
                    print("DLT Function")
                    args=concatArguments(message)
                    messageNumber=args[1]
                    timestamp=args[3:len(args)]
                    index=-1
                    for MSG in messages:
                        if MSG['messageNumber'] == int(messageNumber) and MSG['timestamp'] == timestamp and MSG['username'] == getUsername(clientAddress, clients):
                            index=messages.index(MSG)
                    if index != -1:
                        del messages[index]
                        messages=updateMessageLog(messages)
                        print(f'{getUsername(clientAddress, clients)} deleted a message (#{messageNumber}).')
                    else:
                        print(f'{getUsername(clientAddress, clients)} tried to remove someone elses message (#{messageNumber}).')

                elif command == "EDT":
                    print("EDT Function")
                elif command == "RDM":
                    print("RDM Function")
                elif command == "ATU":
                    print("ATU Function")
                elif command == "OUT":
                    print("OUT Function")
                elif command == "UPD":
                    print("UPD Function")

            connection.sendall(str.encode(serverMessage))
            t_lock.notify()
    connection.close()

while True:
    Client, clientAddress = ServerSocket.accept()
    print('Connected to: ' + clientAddress[0] + ':' + str(clientAddress[1]))
    start_new_thread(threaded_client, (Client, clientAddress))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSocket.close()
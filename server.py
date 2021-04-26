import socket
import os
from _thread import *
import threading
import time
import datetime as dt
import sys
from server_helpers import *

def timeoutHandler(username):
    '''
    Defines action of attempt lockout timer. Sets user's login atttempts back to zero so that they may continue further attempts

    param username the username that has been locked out due to too many attempts
    '''
    global clients
    for user in clients:
        if user['username'] == username:
            user['attemptNo']=0
    print("User may now attempt to login again.")
    

serverPort = int(sys.argv[2]) # server port specified by server owner
attemptsAllowed = int(sys.argv[1]) # attempts allowed specified by server owner

# Argument validity check
if len(sys.argv) < 3:
    print("Invalid number of arguments.")

if attemptsAllowed not in range(1,5):
    print(f"Invalid number of allowed failed consecutive attempt: {attemptsAllowed}. The valid value of argument number is an integer between 1 and 5") 
    sys.exit()

t_lock=threading.Condition()

# will store clients info in this list
clients=[]
# will store messages
messages=[]
# would communicate with clients after every second
UPDATE_INTERVAL= 1
timeout=False
clients = createClientList()

ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '0.0.0.0'
open('userlog.txt', 'w').close()
open('messagelog.txt', 'w').close()
try:
    ServerSocket.bind((host, serverPort))
except socket.error as e:
    print(str(e))

print('Waiting for a Connection..')
ServerSocket.listen(20)


def threaded_client(connection, clientAddress):
    '''
    threading function. Each client thread will call this function

    param connection TCP connection socket
    param clientAddress in format 0.0.0.0:8000
    '''
    global t_lock
    global serverSocket
    global clients
    global messages

    # Loop and listen for data being sent from clients
    while True:
        data = connection.recv(2048)
        message = data.decode().split()
        now=dt.datetime.now().strftime("%d %b %Y %H:%M:%S")
        with t_lock:
            if checkUserStatus(clientAddress, clients) == False:      # if user is not logged in or not a valid username
                username, password, clientUDPPort=message
                validUserAttempts = 0
                authFlag = CheckLoginDetails(username, password) # valid credentials or not
                clients, validUserAttempts=IncrementAttemptNo(username, clients) # increments attempt count for valid username input
                checkUserStatus(username, clients)
                if validUserAttempts == attemptsAllowed and authFlag == False: # if user has entered a valid username but incorrect password consecutively
                    t=threading.Timer(10, timeoutHandler, args=(username,))
                    serverMessage="Login Attempt Limit Reached. Try again in 10 seconds."
                    t.start()
                elif validUserAttempts > attemptsAllowed: # doesn't allow timer to be reset
                    serverMessage="Login Attempt Limit Reached. Try again in 10 seconds."
                else:
                     # time that user logged in
                    date_time = dt.datetime.now().strftime("%d %b %Y %H:%M:%S")
                    if authFlag == True: # if user's authentication is successful, output message and print to userlog.
                        serverMessage="Login Successful"
                        clients=logUserIn(username, clients, date_time, clientAddress, clientUDPPort)
                        userlog = f'{getActiveUsers(clients)}; {date_time}; {username}; {clientAddress[0]}; {clientUDPPort}'
                        f=open("userlog.txt", "a")
                        print(f'{date_time}: Client user {username} with address {clientAddress[0]}:{clientAddress[1]} has successfully logged in.')
                        print(userlog, file=f)              
                        f.close()
                    else: 
                        serverMessage="Login Unsuccessful. Try again."
            else: #if user is already logged in
                command = message[0]
                if command == "MSG": 
                    print(f'{now}: MSG Function has been attempted by {username}')
                    newMSG=newMessage(message, getUsername(clientAddress, clients), len(messages)+1)
                    messages.append(newMSG) # add message to global messages
                    messageNumber=newMSG['messageNumber']
                    timestamp=newMSG['timestamp']
                    usernameMSG=newMSG['username']
                    messageBody=newMSG['message']
                    edited=newMSG['edited']
                    messagelog=f'{messageNumber}; {timestamp}; {usernameMSG}; {messageBody}; {edited}'
                    f=open("messagelog.txt", "a")
                    print(f'{now}: Client user {usernameMSG} posted {messageNumber}: {messageBody}')
                    print(messagelog, file=f)
                    f.close()
                    serverMessage=f'Message posted at {now}'

                elif command == "DLT":
                    print(f'{now}: DLT Function has been attempted by {username}')
                    args=concatArguments(message)
                    print(args)
                    # Checks for valid input
                    try: # if user input is not correct try will fall through and go to except
                        messageNumber=args[0] # get message number from input
                        timestamp=args[2:len(args)] # get timestamp from input
                        index=-1
                        for MSG in messages: # for all messages in global messages, if any one message matches the details specified by client, as well as being created by client
                            if MSG['messageNumber'] == int(messageNumber) and MSG['timestamp'] == timestamp and MSG['username'] == getUsername(clientAddress, clients):
                                index=messages.index(MSG)
                                messageBody=MSG['messageBody']
                        if index != -1: # if index hasn't changed, the message either doesn't exist or is not owned by user
                            del messages[index]
                            messages=updateMessageLog(messages)
                            print(f'{now}: Client user {getUsername(clientAddress, clients)} deleted {messageNumber}: {messageBody}')
                            serverMessage="Message deleted."
                        else: # if the message is not owned by user do nothing but print to output
                            print(f'{now}: Client user {getUsername(clientAddress, clients)} was unsuccessful in deleting {messageNumber}: {messageBody}.')
                    except:
                        serverMessage = "Please enter a valid message number and timestamp to delete a message."

                elif command == "EDT":
                    print(f'{now}: EDT Function has been attempted by {username}')
                    try: # if user input is not correct try will fall through and go to except
                        args=concatArguments(message)
                        messageNumber=args[0] # get message number from input
                        timestamp=args[2:22] # get timestmap from input
                        editMSG=args[23:len(args)] # get message body from input
                        index=-1

                        if int(messageNumber) > len(messages): # if user has input a message number that is greater than the number of messages in list, print error
                            print(f'{now}: Client user {getUsername(clientAddress, clients)} entered an invalid message number {messageNumber}')
                            serverMessage=error
                            connection.sendall(str.encode(serverMessage))
                            t_lock.notify()
                            continue
                        # for all messages in global messages, if message details match with client input as well as being created by client, set index to index of message in list
                        for MSG in messages:
                            if MSG['messageNumber'] == int(messageNumber) and MSG['timestamp'] == timestamp and MSG['username'] == getUsername(clientAddress, clients):
                                index=messages.index(MSG)
                        if index != -1: # otherwise the message exists, index will be set and the message will be edited
                            serverMessage="Edit request"
                            connection.sendall(str.encode(serverMessage))
                            data = connection.recv(2048)
                            confirmation = data.decode().split()
                            if confirmation[0] == "Y":
                                messages[index]['message']=editMSG
                                messages[index]['edited']="yes"
                                updateMessageLog(messages)
                                print(f'{now} Client user {getUsername(clientAddress, clients)} edited a message (#{messageNumber}).')
                                serverMessage="Message Edited"
                            else:
                                print(f'{now} Client user {getUsername(clientAddress, clients)} cancelled editing a message (#{messageNumber}).')
                                serverMessage="Edit cancelled."
                        else: # if index has not been set and is still -1, the user attempted to edit a message that did not create
                            print(f'{now} Client user {getUsername(clientAddress, clients)} tried to edit someone elses message (#{messageNumber}).')
                            serverMessage="Invalid Message Details. You can only edit messages you have posted."
                    except: # invalid input
                        serverMessage="Please enter a valid message number and timestamp to edit a message."
                elif command == "RDM":
                    print(f'{now}: RDM Function has been attempted by {username}')
                    try: # if user input is not correct try will fall through and go to except
                        args=concatArguments(message)
                        message_list = "" # empty string to be filled with messages and returned to client
                        if messages is not None: # as long as global messages isnt empty concatenate messages into a string and send to client
                            for MSG in messages:
                                if MSG["timestamp"] > args: # if the message timestamp is after specified timestamp
                                    messageNumber=MSG['messageNumber']
                                    timestamp=MSG['timestamp']
                                    username=MSG['username']
                                    messageBody=MSG['message']
                                    edited=MSG['edited']
                                    data=f'{messageNumber}; {timestamp}; {username}; {messageBody}; {edited}\n'
                                    message_list=message_list+data
                        if len(message_list) > 0: # remove the last \n in list and set server message
                            serverMessage=message_list[0:-1]
                        else: # if list is empty, return message
                            serverMessage="No messages found after timestamp."
                    except: # invalid input
                        serverMessage="Please enter a valid timestamp to read messages."
                    
                elif command == "ATU":
                    print(f'{now}: ATU Function has been attempted by {username}')
                    user_list="" # empty string to be filled with active users and returned to client 
                    for user in getActiveUserList(clients):
                        if getUsername(clientAddress, clients) != user['username']: # if the user is not equal to the client calling ATU
                            status=user['status']
                            timestamp=user['timestamp']
                            username=user['username']
                            ip=user['addr'][0]
                            port=user['udp_port']
                            data = f'{status}; {timestamp}; {username}; {ip}; {port}\n'
                            user_list=user_list+data
                    if len(user_list) > 0: # remove the last \n in list and set server message
                        serverMessage=user_list[0:-1]
                    else: # if list is empty, return message
                        serverMessage="No active users found."
                elif command == "OUT":
                    print(f'{now}: OUT Function has been attempted by {username}')
                    index=-1
                    serverMessage="Logout request"
                    connection.sendall(str.encode(serverMessage))
                    data = connection.recv(2048)
                    confirmation = data.decode().split()
                    if confirmation[0] == "Y": # ask for confirmation from user
                        for client in clients: # if Y loop through clients and remove them from active users
                            if client['username'] == username: 
                                index=clients.index(client)
                                userID=client['status']
                        clients=updateActiveUsers(clients, userID) # update global clients
                        updateUserLog(clients, userID)     # update userlog.txt
                        serverMessage="Thank you for using our service. Goodbye."
                        print(f'{now}: Client user {username} has logged out')
                        connection.sendall(str.encode(serverMessage))
                        t_lock.notify()
                        connection.close()
                        
                        break
                    else:
                        serverMessage="Logout aborted."
                elif command == "UPD":
                    print(f'{now}: UPD Function has been attempted by {username} check clients for success')

            connection.sendall(str.encode(serverMessage))
            t_lock.notify()
    connection.close()

while True:
    now=dt.datetime.now().strftime("%d %b %Y %H:%M:%S")
    Client, clientAddress = ServerSocket.accept()
    print(f'{now}: Connected to: {clientAddress[0]}:{str(clientAddress[1])}')
    start_new_thread(threaded_client, (Client, clientAddress))
ServerSocket.close()
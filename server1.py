# Sample code for Multi-Threaded Server
#Python 3
# Usage: python3 UDPserver3.py
#coding: utf-8
from socket import *
import threading
import time
import datetime as dt
import sys
from server_helpers import *
#Server will run on this port
serverPort = int(sys.argv[2])
attemptsAllowed = int(sys.argv[1])

t_lock=threading.Condition()

#will store clients info in this list
clients=[]
# would communicate with clients after every second
UPDATE_INTERVAL= 1
timeout=False
timeoutList = []
attemptNo = -1

def timeoutHandler(username):
    global timeoutList
    global attemptNo
    timeoutList.remove(username)
    print("end of timer")
    

def recv_handler():
    global t_lock
    global clients
    global clientSocket
    global serverSocket
    global timeoutList
    global attemptNo
    print('Server is ready for service')
    while(1):
        attemptNo+=1
        if attemptNo == attemptsAllowed:
            timeoutList.append(message[0])
            t=threading.Timer(10, timeoutHandler, args=(message[0],))
            t.start()
            attemptNo=-2
        message, clientAddress = serverSocket.recvfrom(2048)
        #received data from the client, now we know who we are talking with
        message = message.decode().split()
            
        #get lock as we might me accessing some shared data structures
        with t_lock:
            print(attemptNo)
            print(timeoutList)
            if message[0] in timeoutList:
                serverMessage="Login Attempt Limit Reached. Try again in 10 seconds."

            else:
                currtime = dt.datetime.now()
                date_time = currtime.strftime("%d/%m/%Y, %H:%M:%S")
                # print('Received request from', clientAddress[0], 'listening at', clientAddress[1], ':', message, 'at time ', date_time)
                authFlag = CheckLoginDetails(message[0], message[1])

                if authFlag == True:
                    clients.append(clientAddress)
                    serverMessage="Login Successful"
                    print(f'{len(clients)}; {date_time}; {message[0]}; {clientAddress[0]}; {clientAddress[1]}')
                else:
                    serverMessage="Login Unsuccessful. Try again."



            #send message to the client
            serverSocket.sendall(serverMessage.encode(), clientAddress)
            #notify the thread waiting
            t_lock.notify()


def send_handler():
    global t_lock
    global clients
    global clientSocket
    global serverSocket
    global timeout
    #go through the list of the subscribed clients and send them the current time after every 1 second
    while(1):
        #get lock
        with t_lock:
            for i in clients:
                currtime =dt.datetime.now()
                date_time = currtime.strftime("%d/%m/%Y, %H:%M:%S")
                message='Current time is ' + date_time
                clientSocket.sendall(message.encode(), i)
                # print('Sending time to', i[0], 'listening at', i[1], 'at time ', date_time)
            #notify other thread
            t_lock.notify()
        #sleep for UPDATE_INTERVAL
        time.sleep(UPDATE_INTERVAL)

#we will use two sockets, one for sending and one for receiving
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(1)
conn, addr = serverSocket.accept()
print ('Connection address:', addr)

recv_thread=threading.Thread(name="RecvHandler", target=recv_handler)
recv_thread.daemon=True
recv_thread.start()

send_thread=threading.Thread(name="SendHandler",target=send_handler)
send_thread.daemon=True
send_thread.start()
#this is the main thread
while True:
    time.sleep(0.1)


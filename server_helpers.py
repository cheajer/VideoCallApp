import time
import datetime as dt

def ParseLoginDB():
    '''
    Parses credentials.txt

    returns a list of credentials based on credentials.txt
    '''
    f = open("credentials.txt", "r")
    rawDetails = f.read().splitlines()

    details = []

    for x in rawDetails:
        splitStr = x.split()
        user = {'username':splitStr[0],'password':splitStr[1]}
        details.append(user)
    f.close()
    return details

def CheckLoginDetails(username, password):
    '''
    Compares username and password against credentials in credentials.txt

    returns True if matching, False if not
    '''
    details = ParseLoginDB()

    for user in details:
        if user['username'] == username and user['password'] == password:
            return True
        
    return False

def CheckValidUsername(username):
    '''
    Checks if a username exists in credentials.txt

    returns True if yes False if not
    '''
    details = ParseLoginDB()

    for user in details:
        if user['username'] == username:
            return True
        
    return False

def IncrementAttemptNo(username, clients):
    '''
    Increments the number of attempts a user has made at logging in unsuccessfully

    returns an updated client list
    '''
    details = ParseLoginDB()
    returnList = []
    returnNo = 0

    if CheckValidUsername(username):
        for user in clients:
            if user['username'] == username:
                user['attemptNo']+=1
                returnNo=user['attemptNo']

    for user in clients:
        returnList.append(user)
        
    return returnList, returnNo

def createClientList():
    '''
    Parses credentials.txt and creates a client list with all users in credentials.txt

    returns a list of clients based on credentials.txt
    '''
    details = ParseLoginDB()
    clients = []

    for user in details:
        details = {'username':user['username'], 'attemptNo':0, 'status':-1, 'addr': 0, 'timestamp': -1 }
        clients.append(details)
    return clients

def logUserIn(username, clients, date_time, clientAddress, clientUDPPort):
    '''
    Logs a user in given client details. 

    returns an updated client list with new user logged in
    '''
    returnList = []

    for user in clients:
        if user['username'] == username:
            user['status']=getActiveUsers(clients)+1
            user['addr']=clientAddress
            user['udp_port']=clientUDPPort
            user['timestamp'] = date_time
            user['attemptNo']: 0

    for user in clients:
        returnList.append(user)
        
    return returnList

def checkUserStatus(clientAddress, clients):
    '''
    Checks if a user is logged in

    returns True if yes, False if not
    '''
    for user in getActiveUserList(clients):
        if user['addr'] == clientAddress:
            return True
    return False  
   
def getActiveUsers(clients):
    '''
    Getter for active users/ user's with status key not -1 (count)

    returns a count of clients that are currently connected to server
    '''
    count=0
    for user in clients:
        if user['status'] > 0:
            count+=1
    return count

def getActiveUserList(clients):
    '''
    Getter for active users/ user's with status key not -1

    returns a list of clients that are currently connected to server
    '''
    client_list=[]
    for user in clients:
        if user['status'] > 0:
            client_list.append(user)

    return sorted(client_list, key = lambda i: i['status'])


def concatArguments(arguments):
    '''
    Concatenates arguments to be used in functions EDT, DLT, etc.

    returns args minus command
    '''
    args=' '.join(word for word in arguments)
    return args[4:len(args)]

def newMessage(messageBody, username, messageNumber):
    '''
    Creates a new message object that is to be appended to messages list

    returns a message object with keys messageNumber, timestamp, username, message, edited flag
    '''
    date_time=dt.datetime.now().strftime("%d %b %Y %H:%M:%S")
    message = {'messageNumber': messageNumber, 'timestamp': date_time,'username': username, 'message': concatArguments(messageBody), 'edited': "no"}
    return message

def getUsername(clientAddress, clients):
    '''
    Getter for the current client's username

    returns a count of clients that are currently connected to server
    '''
    for client in clients:
        if client['addr'] == clientAddress:
            return client['username']
    return False

def updateMessageLog(messages):
    '''
    Updates message log following deletion, edit of a message

    '''
    date_time=dt.datetime.now().strftime("%d %b %Y %H:%M:%S")
    f=open("messagelog.txt", "w")
    for message in messages:
        messageNumber=message['messageNumber']
        username=message['username']
        messageBody=message['message']
        edited=message['edited']
        messagelog=f'{messageNumber}; {date_time}; {username}; {messageBody}; {edited}'
        print(messagelog, file=f)

def updateUserLog(clients, index):
    '''
    Updates user log following a user logging out or logging in

    '''
    f=open("userlog.txt", "w")
    details=[]
    for client in clients:
        if client['status'] != -1:
            status=client['status']
            timestamp=client['timestamp']
            username=client['username']
            ip=client['addr'][0]
            port=client['udp_port']
            userlog = f'{status}; {timestamp}; {username}; {ip}; {port}'
            print(userlog, file=f)
    f.close()

def updateActiveUsers(clients, index):
    '''
    Updates active users by changing their status to -1 when they log out
    Also increments their status numbers to ensure correct output.

    '''
    returnList = []
    for client in clients:
        if client['status'] == index:
            client['status']=-1
        if client['status'] > index:
            client['status']=client['status']-1
        returnList.append(client)
    return sorted(returnList, key = lambda i: i['status'])
    
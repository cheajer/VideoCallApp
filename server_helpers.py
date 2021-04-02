import time
import datetime as dt

def ParseLoginDB():
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
    details = ParseLoginDB()

    for user in details:
        if user['username'] == username and user['password'] == password:
            return True
        
    return False

def CheckValidUsername(username):
    details = ParseLoginDB()

    for user in details:
        if user['username'] == username:
            return True
        
    return False

def IncrementAttemptNo(username, clients):
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
    details = ParseLoginDB()
    clients = []

    for user in details:
        details = {'username':user['username'], 'attemptNo':0, 'status':"out", 'addr': 0 }
        clients.append(details)
    return clients

def logUserIn(username, clients, clientAddress):
    returnList = []

    for user in clients:
        if user['username'] == username:
            user['status']="in"
            user['addr']=clientAddress

    for user in clients:
        returnList.append(user)
        
    return returnList

def checkUserStatus(clientAddress, clients):
    for user in clients:
        if user['addr'] == clientAddress:
            return True
    return False  
   
def getActiveUsers(clients):
    count=0
    for user in clients:
        if user['status'] == "in":
            count+=1
    return count


def concatArguments(arguments):
    args=' '.join(word for word in arguments)
    return args[4:len(args)]

def newMessage(messageBody, username, messageNumber):
    currtime = dt.datetime.now()
    date_time = currtime.strftime("%d/%m/%Y, %H:%M:%S")
    message = {'messageNumber': messageNumber, 'timestamp': date_time,'username': username, 'message': concatArguments(messageBody), 'edited': "no"}
    return message

def getUsername(clientAddress, clients):
    for client in clients:
        if client['addr'] == clientAddress:
            return client['username']
    return False

def updateMessageLog(messages):
    f=open("messagelog.txt", "w")
    for message in messages:
        messageNumber=message['messageNumber']
        timestamp=message['timestamp']
        username=message['username']
        messageBody=message['message']
        edited=message['edited']
        messagelog=f'{messageNumber}; {timestamp}; {username}; {messageBody}; {edited}'
        print(messagelog, file=f)
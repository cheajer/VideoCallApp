import time

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


import time

def printCommands():
    '''
    Prints valid command string
    '''
    return "Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UPD): "

def checkValidCommand(command):
    '''
    Checks if user input includes a valid command
    '''
    command = command[0:4]
    validCommands = ["MSG ", "DLT ", "EDT ", "RDM ", "ATU", "OUT", "UPD "]
    if command not in validCommands:
        return False
    return True

def getPortbyUsername(active_users, username):
    '''
    Gets UDP port using client's username
    '''
    for user in active_users:
        splitStr=user.split('; ')
        if str(username) == str(splitStr[2]):
            return splitStr[4]
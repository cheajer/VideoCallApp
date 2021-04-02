import time

def printCommands():
    return "Enter one of the following commands (MSG, DLT, EDT, RDM, ATU, OUT, UPD): "

def checkValidCommand(command):
    command = command[0:3]
    validCommands = ["MSG", "DLT", "EDT", "RDM", "ATU", "OUT", "UPD"]
    if command not in validCommands:
        return False
    return True


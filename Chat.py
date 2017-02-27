# COMP 429
# 2/22/17
# P2P_Chat_App

# Authors:
# Vlad Synnes
# Sam Decanio
# Philip Porter

"""
TODO:
    Stop the connection from closing after a single message - move disconnect to separate function (only called on command)
    Create new prompt for when user connects that send list of other users connected

Layout of Interaction with user:
    User runs client
    Upon running the client


handling of local user commands
handling of commands/messages from other users
"""



import socket
import threading
import os

bind_ip = "127.0.0.1"
bind_port = 9980
connections = {}

#used instead of magic numbers when accessing values in dictionary
IP = 0
PORT = 1
SOCKET = 2

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(100)

print("[*] Listening on %s:%d" % (bind_ip, bind_port))

#waiting for incoming clients
def handle_incoming():
    print("Incoming Handler Thread Launched.")
    while True:
        client, addr = server.accept()
        print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))
        #add to list of connections, return list of current connections
        #ready client thread to handle incoming data
        incoming_client_handler = threading.Thread(target=handle_incoming_client, args=(client, addr))
        incoming_client_handler.start()

def join(request, client, addr):
    split = request.split(' ')
    username = split[1]
    #TO FIX: we shouldn't just chop off the last two before we check if they are actually a carriage return
    # and line break - sometimes they are not
    username = username[:len(username) - 2]  # removing the carriage return and new line from end of word
    print("[*] username: %s" % username)
    #check if the username is valid
    if validate_username(client, username):
        #good username, add to connections list
        connections[username] = [addr[0], addr[1], client]
        print("Added: connections[%s] = %s" % (username, connections[username]))
        return True
    return False

def users(request, client):
    print("users called.")
    #this will display a list of users (basically iterate the dictionary)
    try:
        userList = []
        userList.append('USERS ')
        for key, value in connections.items():
            print("key = %s --> values = %s" % (key, value))
            userList.append('' + key + ' ' + str(value[IP]) + ' ' + str(value[PORT]) + '\r\n')
        userListStr = ''.join(userList)
        print(userListStr)
        client.send(userListStr.encode())
        return True
    except Exception:
        return False


def validate_username(client, username):
    #check if the username meets length requirements, and is not taken
    if not(len(username) > 4 and len(username) < 32):
        #we send an invalid username response
        client.send("INVALID USERNAME\r\n".encode())
        return False
    elif username in connections.keys():
        client.send("USERNAME TAKEN\r\n".encode())
        return False

    for char in username:
        if ord(char) not in range(33, 126):
            client.send("INVALID USERNAME\r\n".encode())
            return False

    return True

#incoming client handling thread - we need to make this iterative
def handle_incoming_client(client, addr):
    request = client.recv(4096).decode('utf-8')
    print("[*] Received: %s" % request)
    if request.startswith('JOIN '):
        if join(request, client, addr):
            if not users(request, client):
                client.send("Error: Failed to retrieve list of active users. Please try again.\r\n")
        else:
            client.send("Error: Failed to validate username and join connection. Please try again.\r\n".encode())
    elif request.startswith('GET_USERS'):
        if not users(request, client):
            client.send("Error: Failed to retrieve list of active users. Please try again.\r\n")
    elif request.startswith(''):
        print("Placeholder")
    client.close()

#handle user input
def handle_user():
    print("Handle User Thread Launched")
    cont = True
    while cont:
        command = input(">>> ")
        if command == 'quit':
            quit()

#exit the client
def quit():
    #we should add something in here that sends a message to all connections to close this connection
    exit(0)

print("Welcome to our P2P Chat Client.\n")
incoming_handler = threading.Thread(target=handle_incoming, args=())
incoming_handler.start()
user_handler = threading.Thread(target=handle_user, args=())
user_handler.start()





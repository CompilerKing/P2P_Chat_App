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
bind_port = 9984
connections = {}

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
        new_connection(client, addr)
        #add to list of connections, return list of current connections
        # ready client thread to handle incoming data
        incoming_client_handler = threading.Thread(target=handle_incoming_client, args=(client, addr))
        incoming_client_handler.start()

def new_connection(client, addr):
    #get the username of the new connection
    request = client.recv(4096).decode('utf-8')
    if request.startswith('JOIN '):
        split = request.split(' ')
        username = split[1]
        username = username[:len(username) - 2]  # removing the carriage return from end of word
        print("[*] username: %s" % username)
        #check if the username is valid
        if validate_username(client, username):
            #good username, add to connections list
            connections[username] = [addr[0], addr[1]]
            print("added: connections[%s] = %s" % (username, connections[username]))
            #we must send our list of connections back to this person


def validate_username(client, username):
    #check if the username meets length requirements, and is not taken
    if not(len(username) > 4 and len(username) < 32):
        #we send an invalid username response
        client.send("INVALID USERNAME1".encode())
        return False
    elif username in connections.keys():
        client.send("USERNAME TAKEN".encode())
        return False

    for char in username:
        if ord(char) not in range(33, 126):
            client.send("INVALID USERNAME2".encode())
            return False

    return True

#incoming client handling thread
def handle_incoming_client(client_socket, addr):
    request = client_socket.recv(4096).decode('utf-8')
    print("[*] Received: %s" % request)
    client_socket.close()

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





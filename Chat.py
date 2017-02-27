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

#cd /d C:\Users\owner\Desktop\COMP429\P2P_Chat_App
import sys
import socket
import threading
import os
import datetime

bind_ip = "127.0.0.1"
bind_port = 9984
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
        username = username[:len(username)]  # removing the carriage return from end of word
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
        client.send("INVALID USERNAME1\r\n".encode())
        return False
    elif username in connections.keys():
        client.send("USERNAME TAKEN\r\n".encode())
        return False

    for char in username:
        if ord(char) not in range(33, 126):
            client.send("INVALID USERNAME2\r\n".encode())
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
    print("Date: " + datetime.datetime.now().strftime('%H:%M:%S') + "")
    cont = True
    while cont:
        data = input(">>> ")
        if data == "h":
            print("-h : ​List all commands \r\n")
            print("-l : ​List all users currently online\r\n")
            print("-lc​: List all chat rooms\r\n")
            print("-c <chatroom name>:​ enter a specified chatroom\r\n")
            print("-ce <chatroom name>:​ Disconnect from specified chat room\r\n")
            print("-e :​ Exit client\r\n")
            print("-a <contents> : ​Sends message to all connected peers\r\n")
            print("-s <recipient> <contents> : ​Send the specified contents to the listed recipient(s)\r\n")
            print("-u “username” : ​Pick username for client\r\n")
            print("-o <port> : ​Specify the port to listen on\r\n")
            print("-p:​ Toggle between being listed as p​rivate or being listed as p​ublic\r\n")
            print("-i “username” : ​Ignore a specific user.\r\n")
        if data == "e":
            sys.exit()
        if data.startswith('a') == True and username is not None:
            #send messages here
            print("Date: " + datetime.datetime.now().strftime('%H:%M:%S') + "")
            print("" + username + ": " + data[2:] + "")
        if data.startswith('s') == True:
            #send messages to listed recipients here
            print("Date: " + message + ' (' + datetime.datetime.now().strftime('%H:%M:%S') + ')')
            print("" + username + ": " + data[2:] + "")
        if data.startswith('u') == True:
            print("Enter your username:\r\n")
            request = client_socket.recv(4096).decode('utf-8')
            validate_username(client,username)
        if data.startswith('0') == True:
            port = data[2:]
        if data.startswith('p') == True:
            print("Toggle privacy\r\n")
            #private toggle...
        if data.startswith('i') == True:
            print("Ignore feature\r\n")
            #ignore command...
        else:
            break

print("Welcome to our P2P Chat Client.\n")
incoming_handler = threading.Thread(target=handle_incoming, args=())
incoming_handler.start()
user_handler = threading.Thread(target=handle_user, args=())
user_handler.start()




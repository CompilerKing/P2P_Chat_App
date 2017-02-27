# COMP 429
# 2/22/17
# P2P_Chat_App

# Authors:
# Vlad Synnes
# Sam Decanio
# Philip Porter

import socket
import threading
import os

bind_ip = "127.0.0.1"
bind_port = 9977
connections = {}

# used instead of magic numbers when accessing values in dictionary
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
        #ready client thread to handle incoming data
        incoming_client_handler = threading.Thread(target=handle_incoming_client, args=(client, addr))
        incoming_client_handler.start()

def join(request):
    split = request.split(' ')
    split_username = split[1]
    split_ip = split[2]
    split_port = split[3]
    print("<--- username = %s, ip = %s, port = %s" % (split_username, split_ip, split_port))
    client_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_send.connect((split_ip, int(split_port)))
    #check if the username is valid
    valid = validate_username(split_username)
    if  valid == 0:
        #good username, add to connections list
        connections[split_username] = [split_ip, split_port, client_send]
        print("Added: connections[%s] = %s" % (split_username, connections[split_username]))
        return client_send
    elif valid == -1:
        client_send.send("INVALID USERNAME".encode())
    elif valid == -2:
        client_send.send("USERNAME TAKEN".encode())

    return False

def users(client_send):
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
        client_send.send(userListStr.encode())
        return True
    except Exception:
        return False


def validate_username(username):
    #check if the username meets length requirements, and is not taken
    if not(len(username) > 4 and len(username) < 32):
        #we send an invalid username response
        return -1
    elif username in connections.keys():
        return -2

    for char in username:
        if ord(char) not in range(33, 126):
            return -1

    return 0

#incoming client handling thread - we need to make this iterative
def handle_incoming_client(client, addr):
    request = client.recv(4096).decode('utf-8')
    print("[*] Received: %s" % request)
    if request.startswith('JOIN '):
        send = join(request)
        users(send)
    elif request.startswith('GET_USERS'):
        users(request)
    elif request.startswith('CONNECT '):
        print(" ")
    elif request.startswith('DATA\r\n'):
        print("PLACEHOLDER")
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





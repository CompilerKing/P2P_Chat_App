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
import sys
import re
import datetime

#cd /d C:\Users\owner\Desktop\COMP429\P2P_Chat_App

bind_ip = "127.0.0.1"
bind_port = 9977

# Storage for peers
connections = {}
connections_lock = threading.Lock()

# Misc client config data
ignored_users = list()
headers = list()

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


#incoming client handling thread - we need to make this iterative
def handle_incoming_client(client, addr):
    cont = True
    while cont:

        request = client.recv(4096).decode('utf-8')
        print("[*] Received: %s" % request)
        if request.startswith('JOIN '):
            send = join(request)
            users(send)
        elif request.startswith('GET_USERS'):
            users(request)
        elif request.startswith('CONNECT'):
            print(" ")
        elif request.startswith('DATA\r\n'):
            print("PLACEHOLDER")
        client.close()

def validate_username(username):
    # check if the username meets length requirements, and is not taken
    if not (len(username) > 4 and len(username) < 32):
        # we send an invalid username response
        return -1
    elif username in connections.keys():
        return -2

    for char in username:
        if ord(char) not in range(33, 126):
            return -1

    return 0

# Defined protocol functions
# ///////////////////////////

# Function join validates join request and user name, then sends a list of peers to new peer
def join(request):
    split = request.split(' ')
    split_username = split[1]
    split_ip = split[2]
    split_port = split[3]
    print("<--- username = %s, ip = %s, port = %s" % (split_username, split_ip, split_port))
    client_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_send.connect((split_ip, int(split_port)))
    # check if the username is valid
    valid = validate_username(split_username)
    if valid == 0:
        # good username, add to connections list
        connections[split_username] = [split_ip, split_port, client_send]
        print("Added: connections[%s] = %s" % (split_username, connections[split_username]))
        return client_send
    elif valid == -1:
        client_send.send("INVALID USERNAME".encode())
    elif valid == -2:
        client_send.send("USERNAME TAKEN".encode())

    return False

# this function does the same thing as join() except without validating the username since that has
# already been done
def connect_request(request):
    split = request.split(' ')
    split_username = split[1]
    split_ip = split[2]
    split_port = split[3]
    print("<--- username = %s, ip = %s, port = %s" % (split_username, split_ip, split_port))
    client_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_send.connect((split_ip, int(split_port)))
    connections[split_username] = [split_ip, split_port, client_send]

# Function users sends list of users to host connected to client_send socket
def users(client_send):
    print("users called.")
    # this will display a list of users (basically iterate the dictionary)
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
# /////////////////////////
# END protocol functions

# Defined Client functions
# /////////////////////////
def disp_help():
    print("DERP")

def list_users():
    print("DERP")

def list_chatrooms():
    print("DERP")

def enter_chatroom():
    print("DERP")

def exit_chatroom():
    print("DERP")

def exit():
    print("DERP")

# Helper func
# Generates basic SMTP message string using content "msg" and list of type string "headers"
def msg_smtp_gen(msg, headers=None):
    # Check msg for charset violations
    charset_reg = '[\n\u0032-\u0126\u0128-\u0255]*'

    # Make sure that msg contains only printable chars
    m_msg = re.match(charset_reg, msg)

    # make sure that headers only contains printable chars
    if headers is not None:
        for header in headers:
            m_headers = re.match(charset_reg, header)
            if m_headers is None:
                print("\nERROR: non-printable text in header.\n")
                return None

    if m_msg is not None:

        # Make sure msg contains no early terminations
        msg.replace(".\r\n", ". \r\n")

        # Build smtp message
        smtp_msg = "DATA\r\n" + "Date: " + datetime.datetime.now().strftime('%H:%M:%S') + "\r\n"

        # Add headers
        if headers is not None:
            for header in headers:
                smtp_msg += header + "\r\n"

        # Empty line, add msg, and terminate
        smtp_msg += "\r\n" + msg + ".\r\n"

        return smtp_msg
    else:
        return None

# Function uses global dict "connections" and sends message to each member using already opened
# sockets. Must use SMTP format
def send_all(msg):
    smtp_msg = msg_smtp_gen(msg)

    if smtp_msg is not None:
        # Obtain lock on connections mutex
        connections_lock.acquire()

        # Iterate over all known peers
        for key in connections.keys():
            connections[key][SOCKET].send(smtp_msg.encode())

        # Release lock on connections
        connections_lock.release()

    else:
        print("\nERROR: Message contains invalid characters\n")
        return -1

def send_user(msg, user):
    smtp_msg = msg_smtp_gen(msg)

    if smtp_msg is not None:
        # Obtain lock on connections mutex
        connections_lock.acquire()

        # Validate user to send to
        if connections[user] is not None:
            connections[user][SOCKET].send(smtp_msg.encode())

        else:
            print("\nERROR: User: \"%s\" does not exist\n" % user)
            return -1

        # Release lock on connections
        connections_lock.release()

    else:
        print("\nERROR: Message contains invalid characters\n")
        return -1

def set_username(name):
    print("DERP")

def set_listen_port(port):
    print("DERP")

def toggle_privacy_status():
    if "PRIVATE" in headers:
        headers.remove("PRIVATE")
        print("\nUser now public.\n")
    else:
        headers.append("PRIVATE")
        print("\nUser now Private.\n")

def ignore_user():
    print("DERP")

# END client functions



#handle user input :: UI
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

        if data.startswith('a') == True:
            # Get message
            message = data.split(' ')[1]

            # Send to all connections
            send_all(message)

            # Client terminal echo
            print("\nDate: " + message + ' (' + datetime.datetime.now().strftime('%H:%M:%S') + ')')
            print("\n" + username + ": " + data[2:] + "")

        if data.startswith('s') == True:
            # Get username
            username = data.split(' ')[1]

            # Get message
            message = data.split(' ')[2]

            # Send message
            send_user(message, username)

            # Client terminal echo
            print("\nDate: " + message + ' (' + datetime.datetime.now().strftime('%H:%M:%S') + ')')
            print("\n" + username + ": " + data[2:] + "")

        if data.startswith('u') == True:
            username = data.split(' ')[1]
            set_username(username)

        if data.startswith('o') == True:
            new_port = int(data.split(' ')[1])
            set_listen_port(new_port)

        if data.startswith('p') == True:
            print("\nToggle privacy\n")
            #private toggle...

            toggle_privacy_status()

        if data.startswith('i') == True:
            print("Ignore feature\r\n")
            #ignore command...

            username = data.split(' ')[1]
            ignore_user(username)

        else:
            break

print("Welcome to our P2P Chat Client.\n")

# Thread for handling incoming connections :: Server thread
incoming_handler = threading.Thread(target=handle_incoming, args=())
incoming_handler.start()

# Thread for handling user input           :: Local User interface Thread
user_handler = threading.Thread(target=handle_user, args=())
user_handler.start()
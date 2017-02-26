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

import socket
import threading
import sys
import os
import datetime

bind_ip = "127.0.0.1"
bind_port = 9997
connections = dict()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(100)

def handle_incoming():
    print("Incoming Handler Thread Launched.")
    while True:
        # we need to add the incoming connection to our list of connections
        client, addr = server.accept()
        print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))
        # ready client thread to handle incoming data
        incoming_client_handler = threading.Thread(target=handle_incoming_client, args=(client,))
        incoming_client_handler.start()

print("[*] Listening on %s:%d" % (bind_ip, bind_port))

#incoming client handling thread
def handle_incoming_client(client_socket):
    request = client_socket.recv(1024)
    print("[*] Received: %s" % request)
    client_socket.send("Received: %s\n" % request)
    client_socket.close()

def username_check(username):
    for i in range(10000):
        check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = check.connect_ex((remoteServerIP, i))
        # if result show username, IP and port
        if result == username:
            print("USERNAME TAKEN\r\n")
        sock.close()

def handle_user():
    print("Handle User Thread Launched")
    print("Date: " + datetime.datetime.now().strftime('%H:%M:%S') + "")
    cont = True
    while cont:
        data = input(">>>\r\n")
        while data is not None:
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
                exit()
            if data.startswith('a') == True and username is not None:
                #send messages here
                print("Date: " + datetime.datetime.now().strftime('%H:%M:%S') + "")
                print("" + username + ": " + data[2:] + "")
            if data.startswith('s') == True:
                #send messages to listed recipients here
                print("Date: " + message + ' (' + datetime.datetime.now().strftime('%H:%M:%S') + ')')
                print("" + username + ": " + data[2:] + "")
            if data.startswith('u') == True:
                print("Enter yout username:\r\n")
                username = self.sock.recv(1024)
                username_check(username)
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
    time.sleep(0)

print("Welcome to our P2P Chat Client.\n")
incoming_handler = threading.Thread(target=handle_incoming, args=())
incoming_handler.start()
user_handler = threading.Thread(target=handle_user, args=())
user_handler.start()

    #ready client thread to handle incoming data
    #client_handler = threading.Thread(target=handle_client,args=(client,))
    #client_handler.start()

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
import sys
import os

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

def handle_user():
    print("Handle User Thread Launched")
    cont = True
    while cont:
        command = input(">>> ")
        if command == 'quit':
            quit()

def quit():
    os._exit(0)

print("Welcome to our P2P Chat Client.\n")
incoming_handler = threading.Thread(target=handle_incoming, args=())
incoming_handler.start()
user_handler = threading.Thread(target=handle_user, args=())
user_handler.start()





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

"""



import socket
import threading
import re

bind_ip = "127.0.0.1"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(100)

print("[*] Listening on %s:%d" % (bind_ip, bind_port))

# Storage for list of connected users
# Dict containing USER :: {IP, port}, with data types String :: {String, int}
peers = dict()

# Mutex to protect the dictionary
peer_lock = threading.Lock()

# Check user name
def check_user_name(name):
    MAX_size = 32
    MIN_size = 4
    count = 0

    for c in name:
        if c not in range(33,126):
            return False
        count = count + 1

    return (count >= MIN_size) & (count <= MAX_size)

#function that is used to take input from the client
def take_input(client_socket):
    data = client_socket.recv(1024).decode('utf-8')

    while re.match('[a-zA-Z0-9.\n{}|]*\r\n', data) is None:
        data = data + client_socket.recv(1024).decode('utf-8')
        print(data)

    return data

#function to send output
def send_output(client_socket, data):
    client_socket.send(data.encode())
    return

# client handling thread
def handle_client(client_socket):

    # Server response
    client_socket.send("USERS")

    # obtain lock
    peer_lock.acquire()

    for key in peers.keys():
        send_output(client_socket," %s %s %d" % (key, peers[key][0], peers[key][1]))
    send_output(client_socket,"\r\n")

    # enter interactive loop
    while True:
        msg = take_input(client_socket)

        if msg is "EXIT":
            client_socket.close()
            return # Kills the thread by terminating the target func

while True:
    client, addr = server.accept()
    print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

    # must perform handshake for complete connection
    # this grabs input until terminating sequence is received
    msg = take_input(client)

    matching = re.match('JOIN ([a-zA-Z]*) ([0-9].[0-9].[0-9].[0-9]) ([0-9]*)\r\n',msg)

    # Grab lock
    peer_lock.acquire()

    if matching is not None:
        # Must check for name in peers
        if peers[matching.group(0)] is None:
            peers[matching.group(0)] = {matching.group(1), matching.group(2)}

            # ready client thread to handle incoming data
            client_handler = threading.Thread(target=handle_client, args=(client,))
            client_handler.start()

            peer_lock.release()
        else:
            # Error here
            peer_lock.release()
    else:
        # error here
        peer_lock.release()

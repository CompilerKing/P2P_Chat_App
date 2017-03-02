# COMP 429
# 2/22/17
# P2P_Chat_App

# Authors:
# Vlad Synnes
# Sam Decanio
# Philip Porter
import multiprocessing
import socket
import threading
import sys
import re
import datetime
import os
from time import sleep

from P2P_chat_UI import Chat_UI_Process

#cd /d C:\Users\owner\Desktop\COMP429\P2P_Chat_App

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

    # Default name for user before join or connect
    remote_username = addr[0]
    got_name = False

    cont = True
    while cont:

        request = client.recv(4096).decode('utf-8')
        print("[*] Received: %s" % request)
        if request.startswith('JOIN'):
            # Join func handles JOIN from incoming client
            # func newly opened socket and returns name of client
            send, remote_username = join(request)
            if send is not None:
                users(send)
                remote_username = send
                got_name = True

        elif request.startswith('GET_USERS'):
            users(request)

        elif request.startswith('USERS'):
            populate_connections(request)

        elif request.startswith('CONNECT'):
            remote_username = connect_request(request)
            got_name = True

        elif request.startswith('DATA'):
            if not got_name:
                # Lookup name via peer dict
                for key in connections.keys():
                    if (connections[key][IP] == addr[0]) & (connections[key][PORT] == addr[1]):
                        # Found name
                        remote_username = key
                        got_name = True
                # If true, connected host is sending data before any other contact
                if not got_name:
                    remote_username = "ANON_" + remote_username

            read_data(request, remote_username)
        elif request == "LEAVE\r\n":
            # Remove entry from dict
            connections_lock.acquire()
            connections.pop(remote_username,None)
            connections_lock.release()

            # Update user list
            app_GUI.print_to_user("\n-- %s -- LEAVES CHAT\n" % remote_username)
            app_GUI.set_user_list(connections.keys())

            #Terminate thread and close socket
            client.close()
            cont = False

        # Terminate thread and close socket
        elif request == "":
            client.close()
            cont = False

def validate_username(username):
    if username in connections.keys():
        return -2
    else:
        m = re.match('[\u0021-\u007E]{4,32}', username )
        if m is None:
            return -1
    return 0

# Defined protocol functions
# ///////////////////////////

# Function join validates join request and user name, then sends a list of peers to new peer
def join(request):
    match = re.match('JOIN ([\u0021-\u007E]{4,32}) ([0-9]{1,3}(?:\.[0-9]{1,3}){3}) ([0-9]{1,5})\r\n', request)
    if match is not None:
        split_username = match.group(1)
        split_ip = match.group(2)
        split_port = match.group(3)

        print("Server-request: JOIN")
        print("<--- username = %s, ip = %s, port = %s" % (split_username, split_ip, split_port))
        client_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_send.connect((split_ip, int(split_port)))
        # check if the username is valid
        valid = validate_username(split_username)
        if valid == 0:
            # good username, add to connections list
            connections[split_username] = [split_ip, int(split_port), client_send]
            print("Added: connections[%s] = %s:%d" % (split_username,
                                                      connections[split_username][IP],
                                                      connections[split_username][PORT]))

            # Update list of users
            app_GUI.set_user_list(connections.keys())

            return client_send, split_username
        elif valid == -1:
            client_send.send("INVALID USERNAME\r\n".encode())
            print("JOIN failure, username invalid.")
        elif valid == -2:
            client_send.send("USERNAME TAKEN\r\n".encode())
            # Error
            print("JOIN failure, username taken.")

        return None, ""
    else:
        print("\nIll formed request: %s" % request)

# this function does the same thing as join() except without validating the username since that has
# already been done
def connect_request(request):
    match = re.match('CONNECT ([\u0021-\u007E]{4,32}) ([0-9]{1,3}(?:\.[0-9]{1,3}){3}) ([0-9]{1,5})\r\n', request)
    if match is not None:
        split_username = match.group(1)
        split_ip = match.group(2)
        split_port = match.group(3)
        print("<--- username = %s, ip = %s, port = %s" % (split_username, split_ip, split_port))
        client_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_send.connect((split_ip, int(split_port)))


        connections[split_username] = [split_ip, int(split_port), client_send]
        return split_username
    else:
        print("\nIll formed request: %s" % request)

# Function users sends list of users to host connected to client_send socket
def users(client_send):
    print("Users called:\n")
    # this will display a list of users (basically iterate the dictionary)
    try:
        userListStr = "USERS "

        for key in connections.keys():
            userListStr += "%s %s %d\r\n" % (key, connections[key][IP], connections[key][PORT])

        print("Sent list:\n" + userListStr)
        client_send.send(userListStr.encode())
        return True
    except Exception:
        return False

# Function to set connections dict
def populate_connections(request):

    # Removes head of message, splits by EOL and removes last null entry from list of lines
    user_list_lines = request.replace('USERS ', '').split("\r\n")[:-1]

    print(user_list_lines)

    cont_readUsers = True
    while (len(user_list_lines) > 0) and cont_readUsers:
        match = re.match('([\u0021-\u007E]{4,32}) ([0-9]{1,3}(?:\.[0-9]{1,3}){3}) ([0-9]{1,5})',
                         user_list_lines.pop(0))
        if match is not None:
            user = match.group(1)
            c_ip = match.group(2)
            c_port = match.group(3)

            if user not in connections.keys():
                # Open socket
                client_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_send.connect((c_ip, int(c_port)))

                # Add to connections
                connections[user] = [c_ip, int(c_port), client_send]

                # Send connect request
                client_send.send(("CONNECT " + local_username + " " + bind_ip + " " + str(bind_port) + "\r\n").encode())

        else:
            print("\nIll formed USERS message %s" % request)
            cont_readUsers = False

    # Update gui to reflect new connections
    app_GUI.set_user_list(connections.keys())

# Function forwards data to local user
def read_data(data_msg, sender_name):
    # Check msg for charset violations
    # reg for any number of lines
    headers_reg = 'DATA\r\n([\n\u0020-\u007E\u0080-\u00FF]*\r\n)*\r\n'
    data_message_reg = headers_reg + '(([\n\u0020-\u007E\u0080-\u00FF]*(\r\n)*)*)\r\n\.\r\n'

    match = re.match(data_message_reg, data_msg)
    if match is not None:
        app_GUI.print_to_user(("\n\n[%s]:"%sender_name) + match.group(2).
              replace("\n", "").  # Removes all newlines
              replace("\r", "\n"))  # Makes carriage returns newlines
        # This cleans up output to GUI
    else:
        print("\nReceived malformed data message from user")


# /////////////////////////
# END protocol functions

# Defined Client functions
# /////////////////////////
def list_users():
    # Add header to list
    user_list_msg = "\nUser List:\n"

    # Make list
    for key in connections.keys():
        user_list_msg += "%-32s %15s %d\r\n" % (key, connections[key][IP], connections[key][PORT])

    # Print to GUI
    app_GUI.print_to_user(user_list_msg + "\n\r")

def join_network(request):
    split = request.split(' ')
    split_ip = split[1]
    split_port = split[2]
    print("Begin join attempt")
    print("<--- username = %s, ip = %s, port = %s" % (local_username, bind_ip, int(bind_port)))
    client_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_send.connect((split_ip, int(split_port)))


    join_msg = "JOIN " + local_username + " " + bind_ip + " " + str(bind_port) + "\r\n"
    client_send.send(join_msg.encode())
    client_send.close()

    return True

def exit_client():
    # Send leave to all peers
    leave_client()

    # kill thread
    sys.exit()

def leave_client():
    # Send leave to all peers
    connections_lock.acquire()
    for key in connections.keys():
        if connections[key][SOCKET] is not None and key is not local_username:
            connections[key][SOCKET].send("LEAVE\r\n".encode())
            # Close socket
            connections[key][SOCKET].close()

    connections_lock.release()
    # update client list
    app_GUI.set_user_list(connections.keys())

# Helper func
# Generates basic SMTP message string using content "msg" and list of type string "headers"
def msg_smtp_gen(msg, headers=None):
    # Check msg for charset violations
    charset_reg = '([\n\u0020-\u007E\u0080-\u00FF]*(\r\n)*)*'

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
        smtp_msg += "\r\n" + msg + "\r\n.\r\n"

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

        # Echo to GUI
        app_GUI.print_to_user("\n[%s]:%s" % (local_username, msg))

        # Iterate over all known peers
        for key in connections.keys():
            if key != local_username:
                connections[key][SOCKET].send(smtp_msg.encode())

        # Release lock on connections
        connections_lock.release()

    else:
        app_GUI.print_to_user("\nERROR: Message contains invalid characters\n")
        return -1

def send_user(msg, user):
    smtp_msg = msg_smtp_gen(msg)

    if smtp_msg is not None:
        # Obtain lock on connections mutex
        connections_lock.acquire()

        # Validate user to send to
        if user in connections.keys():
            # Send message
            connections[user][SOCKET].send(smtp_msg.encode())

            # Echo to GUI
            app_GUI.print_to_user("\n[%s]:%s" % (local_username, msg))

        else:
            app_GUI.print_to_user("\nERROR: User: \"%s\" does not exist\n" % user)
            return -1

        # Release lock on connections
        connections_lock.release()

    else:
        app_GUI.print_to_user("\nERROR: Message contains invalid characters\n")
        return -1

def ignore_user(username):
    if username in ignored_users:
        ignored_users.remove(username)
        app_GUI.print_to_user("\nUser \"%s\" Now not ignored.")
    else:
        ignored_users.insert(0, username)
        app_GUI.print_to_user("\nUser \"%s\" Now ignored.")

# END client functions

#handle user input :: UI
def handle_user():
    print("Handle User Thread Launched")
    print("Date: " + datetime.datetime.now().strftime('%H:%M:%S') + "")

    cont = True

    while cont:
        data = app_GUI.get_output_string()

        if data == "\u0001e":
            # GUI force exit
            exit_client()
        else:
            print("INPUT FROM GUI \"" + data + "\"")

        if data == "h":
            app_GUI.print_to_user("\nHELP list of commands\r\n")
            app_GUI.print_to_user("h : ​List all commands \r\n")
            app_GUI.print_to_user("l : ​List all users currently online\r\n")
            app_GUI.print_to_user("lc​: List all chat rooms\r\n")
            app_GUI.print_to_user("j​: <IP, PORT> join chat network at IP\r\n")
            app_GUI.print_to_user("c <chatroom name>:​ enter a specified chatroom\r\n")
            app_GUI.print_to_user("ce <chatroom name>:​ Disconnect from specified chat room\r\n")
            app_GUI.print_to_user("e :​ Exit client\r\n")
            app_GUI.print_to_user("ec: Leave chat\r\n")
            app_GUI.print_to_user("a <contents> : ​Sends message to all connected peers\r\n")
            app_GUI.print_to_user("s <recipient> <contents> : ​Send the specified contents to the listed recipient(s)\r\n")
            app_GUI.print_to_user("p:​ Toggle between being listed as p​rivate or being listed as p​ublic\r\n")
            app_GUI.print_to_user("i “username” : ​Ignore a specific user.\r\n\r\n")

        elif data == "e":
            # user exit
            exit_client()

        elif data == "ec":
            leave_client()

        elif data == "l":
            list_users()

        elif data == "lc":
            app_GUI.print_to_user("")

        elif data.startswith("j"):
            # Call join network func
            join_network(data)

        elif data.startswith("c"):
            app_GUI.print_to_user("\nEnter chatroom, not implemented\n")

        elif data.startswith("ce"):
            app_GUI.print_to_user("\nExit chatroom, not implemented\n")

        elif data.startswith('a'):
            # Get message
            message = data[2:]

            # Send to all connections
            send_all(message)

            # Client terminal echo
            print("\nDate: " + message + ' (' + datetime.datetime.now().strftime('%H:%M:%S') + ')')
            print("Send to all users.\n")

        elif data.startswith('s'):
            data_split = data.split(' ')

            # Get username
            username = data_split[1]

            # Get message
            message = ''.join(data_split[2:])

            # Send message
            send_user(message, username)

            # Server terminal echo
            print("\nDate: " + message + ' (' + datetime.datetime.now().strftime('%H:%M:%S') + ')')
            print("\n" + username + ": " + data[2:] + "")

        elif data.startswith('p'):
            app_GUI.print_to_user("\nToggle privacy, not implemented\n")
            #private toggle...

        elif data.startswith('i'):
            username = data.split(' ')[1]
            ignore_user(username)
        else:
            print("\nINVALID selection \"%s\"\n" % data)
            app_GUI.print_to_user("\nEntry: \"" + data + "\" is invalid")

if __name__ == '__main__':
    # Default values
    bind_ip = "127.0.0.1"
    bind_port = 9977

    # Storage for peers
    connections = {}
    connections_lock = threading.Lock()

    # User data
    local_username = ""

    # Misc client config data
    ignored_users = list()
    headers = list()

    # used instead of magic numbers when accessing values in dictionary
    IP = 0
    PORT = 1
    SOCKET = 2

    # Fix for Unix like operating systems
    # Prevents crash of GUI process
    if os.name != 'nt':  # If not Windows
        multiprocessing.set_start_method('forkserver')

    # GUI process
    app_GUI = Chat_UI_Process()
    app_GUI.start()

    # Initialise values for local_username, and listen port
    app_GUI.print_to_user("Welcome to our P2P Chat Client.\n\n")
    app_GUI.print_to_user("Please enter your username\n")
    local_username = app_GUI.get_output_string()

    # To allow exit from program without zombie process
    if local_username == "\u0001e":
        # Force exit
        exit_client()

    while validate_username(local_username) < 0:
        app_GUI.print_to_user("Selected username is invalid\n")
        app_GUI.print_to_user("\nPlease enter your username\n")
        local_username = app_GUI.get_output_string()

        # Graceful exit
        if local_username == "\u0001e":
            # Force exit
            exit_client()

    app_GUI.print_to_user("Username \"%s\" selected\n" % local_username)
    app_GUI.print_to_user("\nPlease enter [ip port] to listen on\n")
    response = app_GUI.get_output_string()

    if response == "\u0001e":
        # Force exit
        exit_client()

    response_split = response.split(' ')
    bind_ip = response_split[0]
    bind_port = int(response_split[1])

    app_GUI.print_to_user("Selected IP, port %s, %d\n" % (bind_ip ,bind_port))

    # Store self in connections
    connections[local_username] = [bind_ip, bind_port, None]

    # Update gui list of users
    app_GUI.print_to_user("\u0001%s" % local_username)

    # Begin listening on port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(100)

    print("[*] Listening on %s:%d" % (bind_ip, bind_port))

    # Thread for handling incoming connections :: Server thread
    incoming_handler = threading.Thread(target=handle_incoming, args=(), daemon=True)
    incoming_handler.start()

    # Thread for handling user input           :: Local User interface Thread
    user_handler = threading.Thread(target=handle_user, args=(), daemon=True)
    user_handler.start()

    # Signal client readiness to user
    app_GUI.print_to_user("\nClient Initialized and ready:")

    # Join process
    app_GUI.join()






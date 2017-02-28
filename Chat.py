# COMP 429
# 2/22/17
# P2P_Chat_App

# Authors:
# Vlad Synnes
# Sam Decanio
# Philip Porter

import socket
import threading
import sys
import re
import datetime
import functools
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
    cont = True
    while cont:

        request = client.recv(4096).decode('utf-8')
        print("[*] Received: %s" % request)
        if request.startswith('JOIN'):
            send = join(request)
            users(send)
        elif request.startswith('GET_USERS'):
            users(request)
        elif request.startswith('USERS'):
            populate_connections(request)
        elif request.startswith('CONNECT'):
            connect_request(request)
        elif request.startswith('DATA'):
            read_data(request)
        else:
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

# Function to set connections dict
def populate_connections(request):
    user_list = list(request.split(' ')[1:])

    while (len(user_list) > 0):
        user = user_list.pop(0)
        c_ip = user_list.pop(0)
        c_port = user_list.pop(0)

        if user is not local_username:
            if user not in connections.keys():
                # Open socket
                client_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_send.connect((c_ip, int(c_port)))

                # Add to connections
                connections[user] = [c_ip, c_port, client_send]

                # Send connect request
                client_send.send("CONNECT " + user + " " + c_ip + " " + c_port + "\r\n")

# Function forwards data to local user
def read_data(data_msg):

    # Check msg for charset violations
    # reg for any number of lines
    headers_reg = 'DATA\r\n([\n\u0020-\u007E\u0080-\u00FF]*\r\n)*\r\n'
    data_message_reg = headers_reg + '(([\n\u0020-\u007E\u0080-\u00FF]*(\r\n)*)*)\r\n\.\r\n'

    match = re.match(data_message_reg, data_msg)

    if match is not None:
        print(match.group(2).
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
    app_GUI.print_to_user(functools.reduce(lambda x,y: x + "\n" +  y, connections.keys()))

def join_network(request):
    split = request.split(' ')
    split_username = split[1]
    split_ip = split[2]
    print("Begin join attempt")
    print("<--- username = %s, ip = %s, port = %s" % (split_username, split_ip, bind_port))
    client_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_send.connect((split_ip, bind_port))

    # check if the username is valid
    valid = validate_username(split_username)
    if valid == 0:
        # good username, send join request
        join_msg = "JOIN  " + split_username + " " + split_ip + " " + str(bind_port) + "\r\n"
        client_send.send(join_msg.encode())

        # Get users request
        # wait 1 sec?
        sleep(1)

    return True

def list_chatrooms():
    print("DERP")

def enter_chatroom():
    print("DERP")

def exit_chatroom():
    print("DERP")

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

        # Iterate over all known peers
        for key in connections.keys():
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
        if connections[user] is not None:
            connections[user][SOCKET].send(smtp_msg.encode())

        else:
            app_GUI.print_to_user("\nERROR: User: \"%s\" does not exist\n" % user)
            return -1

        # Release lock on connections
        connections_lock.release()

    else:
        app_GUI.print_to_user("\nERROR: Message contains invalid characters\n")
        return -1

def set_username(name):
    print("DERP")

def set_listen_port(port):
    print("DERP")

def toggle_privacy_status():
    if "PRIVATE" in headers:
        headers.remove("PRIVATE")
        app_GUI.print_to_user("\nUser now public.\n")
    else:
        headers.append("PRIVATE")
        app_GUI.print_to_user("\nUser now Private.\n")

def ignore_user(username):
    print("DERP")

# END client functions



#handle user input :: UI
def handle_user():
    print("Handle User Thread Launched")
    print("Date: " + datetime.datetime.now().strftime('%H:%M:%S') + "")

    cont = True

    while cont:
        data = app_GUI.get_output_string()
        print("INPUT FROM GUI \"" + data + "\"")

        if data == "h":
            app_GUI.print_to_user("-h : ​List all commands \r\n")
            app_GUI.print_to_user("-l : ​List all users currently online\r\n")
            app_GUI.print_to_user("-lc​: List all chat rooms\r\n")
            app_GUI.print_to_user("-j​: <username, IP> join chat network at IP\r\n")
            app_GUI.print_to_user("-c <chatroom name>:​ enter a specified chatroom\r\n")
            app_GUI.print_to_user("-ce <chatroom name>:​ Disconnect from specified chat room\r\n")
            app_GUI.print_to_user("-e :​ Exit client\r\n")
            app_GUI.print_to_user("-a <contents> : ​Sends message to all connected peers\r\n")
            app_GUI.print_to_user("-s <recipient> <contents> : ​Send the specified contents to the listed recipient(s)\r\n")
            app_GUI.print_to_user("-o <port> : ​Specify the port to listen on\r\n")
            app_GUI.print_to_user("-p:​ Toggle between being listed as p​rivate or being listed as p​ublic\r\n")
            app_GUI.print_to_user("-i “username” : ​Ignore a specific user.\r\n\r\n")

        elif data == "e":
            sys.exit()

        elif data.startswith("j"):
            # Call join network func
            if join_network(data):
                local_username = data.split(' ')[1]

        elif data.startswith('a'):
            # Get message
            message = data.split(' ')[1]

            # Send to all connections
            send_all(message)

            # Client terminal echo
            print("\nDate: " + message + ' (' + datetime.datetime.now().strftime('%H:%M:%S') + ')')
            print("\nSend to all users.\n")

        elif data.startswith('s'):
            # Get username
            username = data.split(' ')[1]

            # Get message
            message = data.split(' ')[2]

            # Send message
            send_user(message, username)

            # Client terminal echo
            print("\nDate: " + message + ' (' + datetime.datetime.now().strftime('%H:%M:%S') + ')')
            print("\n" + username + ": " + data[2:] + "")

        elif data.startswith('o'):
            new_port = int(data.split(' ')[1])
            set_listen_port(new_port)

        elif data.startswith('p'):
            print("\nToggle privacy\n")
            #private toggle...

            toggle_privacy_status()

        elif data.startswith('i') == True:
            print("Ignore feature\r\n")
            #ignore command...

            username = data.split(' ')[1]
            ignore_user(username)
        else:
            print("\nINVALID selection\n")
            app_GUI.print_to_user("\nEntry: \"" + data + "\" is invalid")

if __name__ == '__main__':
    bind_ip = "10.31.76.149"
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

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(100)

    print("[*] Listening on %s:%d" % (bind_ip, bind_port))

    print("Welcome to our P2P Chat Client.\n")

    # Thread for handling incoming connections :: Server thread
    incoming_handler = threading.Thread(target=handle_incoming, args=())
    incoming_handler.start()

    # GUI process
    app_GUI = Chat_UI_Process()
    app_GUI.start()

    # Thread for handling user input           :: Local User interface Thread
    user_handler = threading.Thread(target=handle_user, args=())
    user_handler.start()

    # Join threads
    incoming_handler.join()
    user_handler.join()
    app_GUI.join()




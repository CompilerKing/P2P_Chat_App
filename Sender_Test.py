__author__ = 'SDecanio'

import socket
import datetime

#This tool can be used to send sample messages to Chat.py application
#The messages are implemented to follow the Protocol's message structure

target_host = input("Please enter your IP Address: ")
target_port = input("Please enter your Port #: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Attempting to connect to %s:%s" % (target_host, target_port))

#connecting to client
try:
    client.connect((target_host, int(target_port)))
    print("Successfully connected to %s:%s" % (target_host, target_port))

    message_type = input("Please enter your message type:\n1 = Join\n2 = Connect\n3 = Users\n4 = Data")
    message = ""

    if message_type == 1 in range(1,4):
        print("Message Type = %d" % message_type)
        username = input("Enter a username: ")
        ip = input("Enter a IP: ")
        port = input("Enter a Port #: ")

        if message_type == 1:
            message = "JOIN " + username + " " + ip + " " + port + "\r\n"
        elif message_type == 2:
            message = "CONNECT " + username + " " + ip + " " + port + "\r\n"
        else:
            message = "USERS " + username + " " + ip + " " + port + "\r\n"
    elif message_type == 4:
        print("Message Type = %d" % message_type)
        msg = input("Enter your message: ")
        message = msg.replace(".\r\n", ". \r\n")
        message = "DATA\r\n" + "Date: " + datetime.datetime.now().strftime('%H:%M:%S') + "\r\n" + msg + "\r\n.\r\n"


    print("Sending: %s" % message)
    client.send(message.encode())

    # receive something back (hopefully)
    response = client.recv(4096)
    print(response)

except Exception as ex:
    print("Unable to connect: %s" % ex)


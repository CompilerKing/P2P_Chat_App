__author__ = 'SDecanio'

import socket
import threading

#this can be run in the background on the port you specify as listening when interacting with Chat.py
#doing so allows you to see the responses sent from Chat.py when using a telnet/RAW connection from terminal

bind_ip = input("Please enter your IP Address: ")
bind_port = input("Please enter your Port #: ")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, int(bind_port)))

server.listen(5)

print("[*] Listening on %s:%d" % (bind_ip, bind_port))


# client handling thread
# listener will listen until it is closed or receives a message saying "quit"
def handle_client(client_socket):
    request = ''
    while request != 'quit':
        request = client_socket.recv(1024)
        print("[*] Received: %s" % request)
    client_socket.close()


while True:
    client, addr = server.accept()
    print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

    # ready client thread to handle incoming data
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()
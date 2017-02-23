# COMP 429
# 2/22/17
# P2P_Chat_App

# Authors:
# Vlad Synnes
# Sam Decanio
# Philip Porter

import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(100)

print("[*] Listening on %s:%d" % (bind_ip, bind_port))


#client handling thread
def handle_client(client_socket):
    request = client_socket.recv(1024)
    print("[*] Received: %s" % request)

    client_socket.send("Received: %s\n" % request)

    client_socket.close()

while True:
    client, addr = server.accept()
    print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

    #ready client thread to handle incoming data
    client_handler = threading.Thread(target=handle_client,args=(client,))
    client_handler.start()

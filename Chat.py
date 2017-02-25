# COMP 429
# 2/22/17
# P2P_Chat_App

# Authors:
# Vlad Synnes
# Sam Decanio
# Philip Porter

import socket
import threading
import time


#cd /d C:\Users\owner\Desktop\COMP429\P2P_Chat_App
bind_ip = "127.0.0.1"
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

def client_receive(client_socket):
	data = self.sock.recv(1024)
	while data is not None:
		if data:
			print("Date: " + message + ' (' + datetime.datetime.now().strftime('%H:%M:%S') + ')')
			print("Username here: " + data)
		else:
			break
	time.sleep(0)

def username_scan():
	for i in range(10000):
		check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		result = check.connect_ex((remoteServerIP, i))
		# if result show username, IP and port
		if result == 1:
			print("Username: IP:  Port:" + port + "")
		sock.close()




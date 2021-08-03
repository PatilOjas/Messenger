from json.decoder import JSONDecodeError
import socket
import threading
import time
import plyer
import json
import re


# A thread operated function continuously printing the server response
def recieverThread(clientSocket, myMessage):
	while True:
		recvdMsg = str(clientSocket.recv(1024).decode())
		try:
			recvdMsg = json.loads(recvdMsg)
			plyer.Fnotification.notify(
				app_name = "Messenger",
				app_icon = "./Icon/messenger_icon.ico",
				title = recvdMsg['sender'],
				message = recvdMsg['message'],
				timeout = 1
			)
			if recvdMsg['online'] == 1:
				print(recvdMsg['message'])
		except JSONDecodeError:
			recvdMsg = re.split(r"\*\|\*", recvdMsg)
			if len(recvdMsg) > 1:
				for chat in recvdMsg:
					print(chat)
			else:
				print(recvdMsg[0])


class Message:
	def __init__(self):
		self.message = None

try:
	# Creates a socket and if it fails, it will raise an error
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("Socket creation successfull!!!")
except socket.error:
	print("Socket creation failed with error", str(socket.error))

# Default port for server 
portNo = 4444

# Connects to server
try:
	clientSocket.connect(("192.168.1.206", portNo))
	print("Connection successfull!!!")
except socket.error:
	print("Failed to connect with error", socket.error)

# Message object to pass changed message to reciever thread
myMessage = Message()

# Initiates recieverThread
readT = threading.Thread(target=recieverThread, args=(clientSocket,myMessage,))
readT.start()

# To get online users, enter showOn
# To get all registered users, enter showAll
# To change the chat, enter change __username__
# To exit, enter _exit_ 
# To get brief of new messages, checkNewMsgs 

while True:
	myMessage.message = input()
	clientSocket.send(myMessage.message.encode())
	if myMessage.message == "_exit_":
		print("Goodbye...")
		quit()
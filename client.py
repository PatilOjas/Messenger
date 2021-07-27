import socket
import threading
from plyer import notification

# A thread operated function continuously printing the server response
def recieverThread(clientSocket):
	while True:
		recvdMsg = clientSocket.recv(1024).decode()
		if recvdMsg == "tlokidz_-b^zkcr-fpc9(jq$-&et)m7f_8^ys3&sdnbt&*dqoj":
			notification.notify(
				title = "Messenger",
				message = "You have got a new message!!!",
				timeout = 1
			)

		else:
			print(recvdMsg)

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

# Initiates recieverThread
readT = threading.Thread(target=recieverThread, args=(clientSocket,))
readT.start()

# To get online users, enter showOn
# To get all registered users, enter showAll
# To change the chat, enter change __username__
# To exit, enter _exit_ 
# To get brief of new messages, checkNewMsgs 

while True:
	message = input()
	clientSocket.send(message.encode())
	if message == "_exit_":
		print("Goodbye...")
		quit()
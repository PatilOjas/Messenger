import socket
import threading

userData = dict()
applicationThread = list()

def log_in(clientIdentifier, trialCounter):
	clientIdentifier.send("Enter your username: ")
	username = str(clientIdentifier.recv(1024)).strip()
	clientIdentifier.send("Enter your password: ")
	password = str(clientIdentifier.recv(1024)).strip()
	trialCounter -= 1
	if userData[username][password] == password:
		clientIdentifier.send("Log in successfull!!!")
		return True
	elif trialCounter >= 0:
		clientIdentifier.send("Invalid credentials!!!\nAttempts left: {}".format(trialCounter))
		log_in(clientIdentifier, trialCounter)
	else:
		clientIdentifier.send("No attempts left try again after sometime!!!")
		return False

def sign_in(clientIdentifier):
	
	clientIdentifier.send("Please write a username for yourself: ")
	username = str(clientIdentifier.recv(1024)).strip()
	
	if username in userData.keys():
		clientIdentifier.send("Username not available!!!\nTry different one")
		sign_in(clientIdentifier)
	else:
		clientIdentifier.send("Password: ")
		password = str(clientIdentifier.recv(1024)).strip()
		
		clientIdentifier.send("Confirm Password: ")
		confirmPassword = str(clientIdentifier.recv(1024)).strip()
		
		if password != confirmPassword:
			clientIdentifier.send("Passwords did not match!!!")
			sign_in(clientIdentifier)
		else:
			clientIdentifier.send("Registration successfull!!!\nWelcome "+ username)
			userData[username][password] = password	
	return True

def Application(clientIdentifier, counter):
	clientIdentifier.send("Select desired alternatives:\n1: to log in\n2: to sign in\nYour choice: ")
	login_or_signin = clientIdentifier.recv(1024)
	if int(login_or_signin) == 1:
		if not log_in(clientIdentifier, 3):
			applicationThread[counter].join()
	elif int(login_or_signin) == 2:
		pass
	else:
		print("Invalid option!!!\nPlease Try again")	


try:
	# Creates a socket and if it fails, it will raise an error
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("Socket creation successfull!!!")
except socket.error:
	print("Socket creation failed with error", str(socket.error))

# Default port for server 
portNo = 4444

# Bind the socket
try:
	serverSocket.bind((socket.gethostname(), portNo))
	print("Socket has been binded at the port 4444")
except socket.error:
	print("Failed to Bind the socket with error", str(socket.error))

# Put the socket in the passive mode
try:
	serverSocket.listen(10)
	print("Server is listening")
except socket.error:
	print("Failed to listen with error", socket.error)

counter = 0

while True:
	# Will put here
	try:
		clientConnection, clientAddr = serverSocket.accept()
		print("Connection established successfully")
	except socket.error:
		print("Connection failed with error", socket.error)

	applicationThread[counter] = threading.Thread(target=Application, args=(clientConnection, counter,))
	applicationThread[counter].start()
	counter += 1
	
import socket
import threading
import sqlite3

userData = dict()
onlineClients = list()
applicationThread = list()

dbConn = sqlite3.connect('messenger.db')
try:
	dbConn.execute('''CREATE TABLE USERDATA (
		username char(50) PRIMARY KEY,
		name char(50), 
		surname char(50),
		password char(50));''')
	print("Table created successfully")
except:
	pass
dbConn.close()

def log_in(clientIdentifier, trialCounter, dbHandler):
	clientIdentifier.send("Enter your username: ".encode())
	username = str(clientIdentifier.recv(1024).decode()).strip()
	clientIdentifier.send("Enter your password: ".encode())
	password = str(clientIdentifier.recv(1024).decode()).strip()
	trialCounter -= 1
	dbHandler.execute("SELECT password from USERDATA where username='{}'".format(username))
	passwordList = dbHandler.fetchall()
	if passwordList[0][0] == password:
		clientIdentifier.send("Log in successfull!!!".encode())
		onlineClients.append(username)
		try:
			userData[username]["clientIdentifier"] = clientIdentifier
		except:
			userData[username] = dict()
			userData[username]["clientIdentifier"] = clientIdentifier
		return username
	elif trialCounter >= 0:
		clientIdentifier.send("Invalid credentials!!!\nAttempts left: {}".format(trialCounter).encode())
		log_in(clientIdentifier, trialCounter)
	else:
		clientIdentifier.send("No attempts left try again after sometime!!!".encode())
		return False

def sign_in(clientIdentifier, dbHandler):
	
	clientIdentifier.send("Please write your first name: ".encode())
	name = str(clientIdentifier.recv(1024).decode()).strip()
	clientIdentifier.send("Please write your surname: ".encode())
	surname = str(clientIdentifier.recv(1024).decode()).strip()
	clientIdentifier.send("Please write a username for yourself: ".encode())
	username = str(clientIdentifier.recv(1024).decode()).strip()
	dbHandler.execute("SELECT username from USERDATA where username ='{}'".format(username))
	usernameList = dbHandler.fetchall()
	if len(usernameList) > 0:
		clientIdentifier.send("Username not available!!!\nTry different one".encode())
		sign_in(clientIdentifier, dbHandler)
	else:
		clientIdentifier.send("Password: ".encode())
		password = str(clientIdentifier.recv(1024).decode()).strip()
		
		clientIdentifier.send("Confirm Password: ".encode())
		confirmPassword = str(clientIdentifier.recv(1024).decode()).strip()
		
		if password != confirmPassword:
			clientIdentifier.send("Passwords did not match!!!".encode())
			sign_in(clientIdentifier, dbHandler)
		else:
			clientIdentifier.send(str("Registration successfull!!!\nWelcome " + username).encode())
			userData[username] = dict()
			dbHandler.execute('''INSERT INTO USERDATA (username, password, name, surname) 
			values ('{}', '{}', '{}', '{}')'''.format(username, password, name, surname))
			userData[username]["clientIdentifier"] = clientIdentifier
			onlineClients.append(username)	
			dbHandler.execute('''CREATE TABLE {} (
				sender char(50), 
				message char(2000),
				date text,
				time text,
				readreciept int,
				FOREIGN KEY (sender) REFERENCES USERDATA(username));'''.format(username))
	return username

def Application(clientIdentifier, counter):
	clientIdentifier.send("Select desired alternatives:\n1: to log in\n2: to sign in\nYour choice: ".encode())
	dbHandler = sqlite3.connect('messenger.db')
	login_or_signin = clientIdentifier.recv(1024).decode()
	if int(login_or_signin) == 1:
		userName = log_in(clientIdentifier, 3, dbHandler.cursor())
		if not userName:
			# applicationThread[counter].join()
			return
	elif int(login_or_signin) == 2:
		userName = sign_in(clientIdentifier, dbHandler.cursor())
		dbHandler.commit()
	else:
		print("Invalid option!!!\nPlease Try again")	
		Application(clientIdentifier, 3)
	
	destClient = userName
	while True:
		recvdMsg = clientIdentifier.recv(1024).decode()
		if recvdMsg == "showOn":
			separator = '\n'
			clientIdentifier.send(separator.join(onlineClients).encode())
			continue
		elif recvdMsg == "showAll":
			separator = '\n'
			clientIdentifier.send(separator.join(userData.keys()).encode())
			continue
		elif recvdMsg.split()[0] == "change":
			# chnage destination client identifier
			if recvdMsg.split()[1] in userData.keys():
				destClient = recvdMsg.split()[1]
				continue
		elif recvdMsg == "_exit_":
			onlineClients.remove(userName)
			print("Connection terminated for", userName)
			# applicationThread[counter].join()
			break
		# destClient.send(recvdMsg.encode())
		dbHandler.execute('''INSERT INTO {} VALUES ('{}', '{}', date(DATETIME('now')), time(DATETIME('now')), 0)'''.format(destClient, userName, recvdMsg))
		dbHandler.commit()

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
	serverSocket.bind(("192.168.1.205", portNo))
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

	applicationThread.append(threading.Thread(target=Application, args=(clientConnection, counter,)))
	applicationThread[counter].start()
	counter += 1

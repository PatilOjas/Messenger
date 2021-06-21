from os import name
import socket
import threading
import psycopg2

onlineClients = list()
applicationThread = list()

dbConn = psycopg2.connect(database="messenger", user="postgres", password="12345678", host="localhost", port=5432)

try:
	dbCursor = dbConn.cursor()
	dbCursor.execute('''CREATE TABLE USERDATA (
		username text PRIMARY KEY,
		name text, 
		surname text,
		password text);''')
	dbConn.commit()
	print("Table created successfully")
except:
	pass

dbConn.close()

def log_in(clientIdentifier, trialCounter, dbCursor, unreadMsgs, unreadChats):
	clientIdentifier.send("Enter your username: ".encode())
	username = str(clientIdentifier.recv(1024).decode()).strip()
	clientIdentifier.send("Enter your password: ".encode())
	password = str(clientIdentifier.recv(1024).decode()).strip()
	trialCounter -= 1
	dbCursor.execute("SELECT password from USERDATA where username='{}'".format(username))
	passwordList = dbCursor.fetchall()
	# Check whether passwordList>0.... To be done
	if len(passwordList) > 0 and passwordList[0][0] == password:
		clientIdentifier.send("Log in successfull!!!".encode())
		onlineClients.append(username)
		dbCursor.execute('''SELECT COUNT(DISTINCT sender), COUNT(sender) from {} 
		where readreciept = 0;'''.format(username))
		readReport = dbCursor.fetchall()
		clientIdentifier.send('''You have {} unread messages from {} chats.'''.format(readReport[0][1], readReport[0][0]).encode())
		unreadMsgs = int(readReport[0][1])
		unreadChats = int(readReport[0][0])

	elif trialCounter >= 0:
		clientIdentifier.send("Invalid credentials!!!\nAttempts left: {}".format(trialCounter).encode())
		username = log_in(clientIdentifier, trialCounter, dbCursor, unreadMsgs, unreadChats)
	else:
		clientIdentifier.send("No attempts left try again after sometime!!!".encode())
		return False
	return username

def sign_in(clientIdentifier, dbCursor):
	clientIdentifier.send("Please write your first name: ".encode())
	name = str(clientIdentifier.recv(1024).decode()).strip()
	clientIdentifier.send("Please write your surname: ".encode())
	surname = str(clientIdentifier.recv(1024).decode()).strip()
	clientIdentifier.send("Please write a username for yourself: ".encode())
	username = str(clientIdentifier.recv(1024).decode()).strip()
	dbCursor.execute("SELECT username from USERDATA where username ='{}'".format(username))
	usernameList = dbCursor.fetchall()
	if len(usernameList) > 0:
		clientIdentifier.send("Username not available!!!\nTry different one".encode())
		username = sign_in(clientIdentifier, dbCursor)
	else:
		clientIdentifier.send("Password: ".encode())
		password = str(clientIdentifier.recv(1024).decode()).strip()
		
		clientIdentifier.send("Confirm Password: ".encode())
		confirmPassword = str(clientIdentifier.recv(1024).decode()).strip()
		
		if password != confirmPassword:
			clientIdentifier.send("Passwords did not match!!!".encode())
			username = sign_in(clientIdentifier, dbCursor)
		else:
			clientIdentifier.send(str("Registration successfull!!!\nWelcome " + username).encode())
			
			dbCursor.execute('''INSERT INTO USERDATA (username, password, name, surname) 
			values ('{}', '{}', '{}', '{}')'''.format(username, password, name, surname))
			
			onlineClients.append(username)	
			dbCursor.execute('''CREATE TABLE {} (
				sender text, 
				message text,
				date text,
				time text,
				readreciept int,
				FOREIGN KEY (sender) REFERENCES USERDATA(username));'''.format(username))
			
	return username

def Application(clientIdentifier, counter):
	clientIdentifier.send("Select desired alternatives:\n1: to log in\n2: to sign in\nYour choice: ".encode())
	dbHandler = psycopg2.connect(database="messenger", user="postgres", password="12345678", host="localhost", port=5432)
	dbCursor = dbHandler.cursor()
	login_or_signin = clientIdentifier.recv(1024).decode()
	unreadMsgs = 0
	unreadChats = 0
	if int(login_or_signin) == 1:
		userName = log_in(clientIdentifier, 3, dbCursor, unreadMsgs, unreadChats)
		if not userName:
			return
	elif int(login_or_signin) == 2:
		userName = sign_in(clientIdentifier, dbCursor)
		dbHandler.commit()
	else:
		print("Invalid option!!!\nPlease Try again")	
		Application(clientIdentifier, 3)
	
	destClient = userName
	while True:

		recvdMsg = clientIdentifier.recv(1024).decode().strip()
		
		if recvdMsg == "showOn":
			separator = '\n'
			clientIdentifier.send(separator.join(onlineClients).encode())
			continue

		elif recvdMsg == "showAll":
			separator = '\n'
			dbCursor.execute("""SELECT username FROM USERDATA;""")
			allUsers = dbCursor.fetchall()
			users = lambda x: [i[0] for i in x]
			clientIdentifier.send(separator.join(users(allUsers)).encode())
			continue

		elif recvdMsg.split()[0] == "change":
			# chnage destination client identifier
			dbCursor.execute('SELECT username FROM USERDATA;')
			allUsers = dbCursor.fetchall()
			users = lambda x: [i[0] for i in x]
			if recvdMsg.split()[1] in users(allUsers): # To be replaced by a SQL statement
				destClient = recvdMsg.split()[1]
				dbCursor.execute("SELECT COUNT(readreciept) FROM {} WHERE sender = '{}';".format(userName, destClient))
				msgsfromsender = int(dbCursor.fetchall()[0][0])
				dbCursor.execute("UPDATE {} SET readreciept = 1 WHERE sender = '{}';".format(userName, destClient))
				unreadMsgs -= msgsfromsender
				unreadChats -= 1
				continue

		elif recvdMsg == "_exit_":
			onlineClients.remove(userName)
			print("Connection terminated for", userName)
			break
		
		elif recvdMsg == "checkNewMsgs":
			dbCursor.execute('''SELECT COUNT(DISTINCT sender), COUNT(sender) from {} 
			where readreciept = 0;'''.format(userName))
			readReport = dbCursor.fetchall()
			clientIdentifier.send('''You have {} unread messages from {} chats.'''.format(readReport[0][1], readReport[0][0]).encode())
			continue
		
		dbCursor.execute('''INSERT INTO {} VALUES ('{}', '{}', CURRENT_DATE, LOCALTIME, 0)'''.format(destClient, userName, recvdMsg))
		dbHandler.commit()

try:
	# Creates a socket and if it fails, it will raise an error
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("Socket creation successfull!!!")
except socket.error:
	print("Socket creation failed with error", str(socket.error))

# Default port for server 
portNo = 4444
# Check what if port 4444 is already in use..?

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
	try:
		clientConnection, clientAddr = serverSocket.accept()
		print("Connection established successfully")
	except socket.error:
		print("Connection failed with error", socket.error)

	applicationThread.append(threading.Thread(target=Application, args=(clientConnection, counter,)))
	applicationThread[counter].start()
	counter += 1

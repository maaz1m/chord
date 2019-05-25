import argparse
import socket
import sys
import threading
import json
import os
import math
import time
from utils import *
from node import *

keystore ={} #The dictionary which holds key values and filenames
	
isRootNode = 1 #Signifies that node is root node 
ownport = int(sys.argv[1])
ownhost = sys.argv[2]

if len(sys.argv)>3:
	rootport = int(sys.argv[3])
	roothost = sys.argv[4]
	root = conc(roothost, rootport)
	isRootNode = 0


# Initiating root node
node = Node(ownhost, ownport)
if isRootNode == 1:
	node.create()
elif isRootNode == 0:
	data = 'JOIN' + '|' + node.name + '|' + str(node.ID)
	sendRequest(root, data)


# Creating a socket for root node
sock = node.listenSocket()	
strBuf = ''
print 'Hash of node is ' + str(node.ID)
# Listener for requests
def reciever():
	while 1:
		conn, addr = sock.accept()
		req = conn.recv(1024)	

		msg = req.split('|')
		if not req:
			break

		elif msg[0] == 'JOIN':
			# JOIN | FROM | ID
			ID = int(msg[2])
			if node.contains(ID):
				data = 'JOINED' + '|' + node.name + '|' + node.pred + '|' + node.succ
				sendRequest(msg[1], data)
				node.updatePred(msg[1])
			else:
				n = node.closestPreceding(ID)
				sendRequest(n, req)

		elif msg[0] == 'JOINED':
			node.setSucc(msg[1])
			node.setPred(msg[2])
			if node.succ == node.pred:
				node.setSuperSucc(node.name)
			else:
				node.setSuperSucc(msg[3])
			node.refreshFingerTable()
	
		elif msg[0] == 'SUCC':
			node.setSuperSucc(node.succ)
			node.setSucc(msg[1])
			data = 'SUPERSUCC|' + msg[1]
			sendRequest(node.pred, data)

		elif msg[0] == 'PRED':
			# PRED | NODE
			node.setPred(msg[1])
			data = 'SUPERSUCC|' + node.succ
			sendRequest(msg[1], data)

		elif msg[0] == 'SUPERSUCC':
			# SUPERSUCC | NODE
			node.setSuperSucc(msg[1])

		elif msg[0] == 'STABILIZE':
			1; #Do nothing

		elif msg[0] == 'STORE':
			# STORE | FROM | ID | FILENAME

			ID = int(msg[2])
			if node.contains(ID):
				# Store file here
				filename = msg[3]
				keystore[str(ID)] = filename
				data = 'DOWNLOAD|' + node.name + '|'+ filename
				sendRequest(msg[1], data)
				data = 'DOWNLOAD|' + node.succ + '|'+ filename
				sendRequest(msg[1], data)

			else:
				sendRequest(node.succ, req)

		elif msg[0] == 'RETRIEVE':
			# RETRIEVE | FROM | ID | FILENAME

			ID = int(msg[2])
			if node.contains(ID):
				# File to be stored is here
				node.sendFile(msg[3], msg[1])
			else:
				sendRequest(node.succ, req)

		elif msg[0] == 'FILLFT':
			# FILLFT | FROM | ID
			ID = int(msg[2])
			if node.contains(ID):
				data = 'FILLEDFT' + '|' + node.name + '|' + msg[2]
				sendRequest(msg[1], data)
			else:
				sendRequest(node.succ, req)

		elif msg[0] == 'FILLEDFT':
			# FILLEDFT | NODE | ID
			ID = int(msg[2])
			node.updateFingerTable(ID, msg[1])

		elif msg[0] == 'DOWNLOAD':
			# DOWNLOAD | FROM | FILENAME
			node.sendFile(msg[2], msg[1])

		elif msg[0] == 'UPLOADING':
			# UPLOADING | FILENAME | CHUNK | i | SIZE
			filename = msg[1]
			chunk = msg[2]
			i = int(msg[3])
			size  = int(msg[4])
			chunk_size = 512
			print 'Downloading ' + str(i) + '/' + str(size)
			if i==0:
				strBuf = chunk
			else:
				strBuf += chunk
			if i>size-chunk_size:
				newfname = filename+'_copy'
				file = open(newfname, 'wb')
				file.write(binascii.unhexlify(strBuf))
				file.close()
			print 'Successfully downloaded ' + filename

		else:
			print "Wrong request type"
			print req
			# sys.exit()	

def displayMenu():
	while 1:
		menu_opt = raw_input("Please select an action:\n \
		1. Store a file\n \
		2. Retrieve a file\n \
		3. Display finger table\n \
		4. Display node details\n \
		5. Exit the program\n ")

		if menu_opt == "1":
			print "Entering file store operation"
			filepath = raw_input("Enter the full path of file you want to store:\nExample: /home/user/filename.txt\n")
			filename = os.path.basename(filepath)
			ID = hashid(filename)
			data = 'STORE' + '|' + node.name + '|' + str(ID) + '|' + filename
			if node.contains(ID):
				keystore[str(ID)] = filename
				print 'File to be stored here'
			else:
				sendRequest(node.succ, data)
				print "Store request sent"

		elif menu_opt == "2":
			print "Performing retrieval of file"
			filename = raw_input("Enter the file to be retreived:\n")
			ID = hashid(filename)
			data = 'RETRIEVE' + '|' + node.name  + '|' + str(ID)  + '|' + filename
			
			if str(ID) in keystore:
				print 'Already have file'
			else: 
				sendRequest(node.succ,data)

		elif menu_opt == "3":
			node.printFingerTable()

		elif menu_opt == "4":
			node.printNode()


		elif menu_opt == "5":
			print "Exiting the program"

		else:
			print "Invalid menu entry"


menu = threading.Thread(target=displayMenu)
menu.start()

def executePeriodically(func, sec):
	#Call func after each sec interval
	def func_wrapper():
		executePeriodically(func, sec)
		func()
	threading.Timer(sec, func_wrapper).start()

executePeriodically(node.stabilize, 5)
executePeriodically(node.refreshFingerTable, 10)

reciever()

	

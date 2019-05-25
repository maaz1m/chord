import argparse
import socket
import sys
import threading
import json
import os
import math
from utils import *

class Finger:
	#Class for each finger table entry
	def __init__(self, id_, node_):
		self.ID = id_
		self.node = node_
	def set(self, node_):
		self.node = node_

class Node:
	#Class that defines the current node
	def __init__(self,hname,hport):
		self.name = conc(hname, hport)
		self.hostname = hname
		self.port = hport
		self.pred = ''
		self.succ = ''
		self.ID = hashid(self.name)
		self.ftableValid = False
		self.initFingerTable()

	def initFingerTable(self):
		#Initialize finger table by setting values for the ID (2^n+1)
		self.ftable = []
		i = (self.ID + 1) % size
		for j in range(k_):
			fing = Finger(i, '')
			self.ftable.append(fing)
			i = (i + 2**j) % size

	def refreshFingerTable(self):
		#Periodic refreshment for finger table
		for f in self.ftable[1:]:
			if self.contains(f.ID):
				f.set(self.name)
			else:
				data = 'FILLFT|'+ self.name + '|' + str(f.ID)
				sendRequest(self.succ, data) 

	def updateOthers(self):
		m = len(self.ftable)
		for i in range(m):
			data = 'FINDPRED' + '|' + self.node + '|' + str(self.ID-(2**i)) + '|' + 'UPDATEFT' + '|' + str(self.id) + '|' + str(i)
			sendRequest(node.pred, data)
			i=i+1

	def updateFingerTable(self, ID, node):
		#Update finger table using the arguments (if applicable)
		self.ftableValid = True
		for f in self.ftable:
			if f.ID == ID:
				f.node = node

	def printFingerTable(self):
		print '-----Current finger table----'
		for f in self.ftable:
			print '   ' + str(f.ID) + ' : ' + f.node
 
	def setSuperSucc(self, ss):
		self.superSucc = ss

	def setSucc(self, succ):
		self.ftable[0].set(succ)
		self.succ = succ

	def setPred(self, pred):
		self.pred = pred

	def create(self):
		#Create DHT with single node (this node)
		self.setSucc(self.name)
		self.setPred(self.name)
		self.setSuperSucc(self.name)
		for f in self.ftable:
			f.set(self.name)

	def contains(self, ID):
		# Check if the current node is responsible for this ID
		if self.succ == self.name:
			return True
		if self.ID == ID:
			return True

		if ID in interval(hashid(self.pred), self.ID, 0, 1):
			return True
		else:
			return False
	def closestPreceding(self, ID):
		#Check finger table to return node closest to the queried ID
		if not ftableValid:
			return self.succ

		for i in range(len(ftable),0, -1):
			if ftable[i].ID <= ID:
				return ftable[i].node

	def updatePred(self, node):
		#Update predecessor with argument
		if self.name == self.pred == self.succ:
			self.setSucc(node)
		else:
			data = 'SUCC' + '|' + node
			sendRequest(self.pred, data)
		self.setPred(node)
	
	def stabilize(self):
		#Check if successor is not dead
		if self.name == self.pred:
			# print 'Checking stability...ok'
			return
		else:
			data = 'STABILIZE|' + self.name
			try:
				sendRequest(self.succ, data)
				# print 'Checking stability...ok'
			except socket.error, msg:
				# print 'Checking stability...error'
				if self.pred == self.succ:
					self.setSucc(self.name)
					self.setPred(self.name)
				else:
					self.setSucc(self.superSucc)
					data = 'SUPERSUCC|' + self.superSucc
					sendRequest(self.pred, data)
					data = 'PRED|' + self.name
					sendRequest(self.succ, data)

	def listenSocket(self):
		#Function for creating a socket on the node to listen.
		global sock	
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error, msg:
			print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
			sys.exit();
		try:
			sock.bind((self.hostname, self.port))
		except socket.error , msg:
			print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message: ' + msg[1]
			sys.exit()
		sock.listen(10)
		return sock
	def printNode(self):
		#Function to print current node positon
		print "Node ID:", self.ID
		print "Predecessor:", self.pred
		print "This node:", self.name
		print "Successor:", self.succ

	def sendFile(self, filename, node):
		#Send file to target node
		file = open(filename,'rb')
		binary_content = file.read()
		file.close()
		ascii_content = binascii.hexlify(binary_content)
		size = len(ascii_content)
		chunk_size = 512
		for i in range(0, size, chunk_size):
			data = 'UPLOADING|' + filename + '|' + ascii_content[i:i+chunk_size] + '|' + str(i) + '|' + str(size) 
			sendRequest(node,data)
		print 'Sent file to ' + node
		

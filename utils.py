import argparse
import socket
import sys
import threading
import json
import os
import math
import binascii

size = 8
k_ = int(math.log(size, 2))

def hashid(key):
	return hash(key)%size

def interval(a , b, leftInclusive = True, rightInclusive = True):
	space = []

	i = a;
	while i != b:
		space.append(i)
		i = (i+1)%size
	space.append(b)
	if not leftInclusive:
		space.remove(a)
	if not rightInclusive:
		space.remove(b)
	return space


def conc(name, port):
	# '192.168.1.1', '8000' -> '192.168.1.1:8000'
	return name + ":" +str(port)

def splt(str):
	# '192.168.1.1:8000' -> '192.168.1.1', '8000'
	return str.split(':')[0],str.split(':')[1]

def sendRequest(node, senddata):
	# Function to send requests and responses to specified targets
	# print 'Sent: ' + senddata + ' to ' + node
	clientHostname, clientPort = splt(node)
	sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	remote_ip = socket.gethostbyname( clientHostname )
	sock2.connect((remote_ip , int(clientPort)))
	sock2.send(senddata)
	sock2.close()

print hash(conc('localhost', 3400))%size
print hash(conc('localhost', 3401))%size
print hash(conc('localhost', 3403))%size


import gameprotocol as gb
import socket
from multiprocessing import Process
import os
import redis
import json


TCP_IP = '127.0.0.1'
TCP_PORT = 20013
BUFFER_SIZE = 20


chessBoard = [	[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0] ]

emptyGameData = json.dumps(chessBoard)


def statsServer():
	r = redis.Redis("localhost")
	CLIENT_KEY = "Clients"
	UDP_IP = "127.0.0.1"
	UDP_PORT = 20014
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((UDP_IP, UDP_PORT))
	#s.listen(1)
	
	while True:
		data, addr = s.recvfrom(1024)
		if data == "<start>\r\nStats: Please\r\n<end>\r\n":
			cls =  json.dumps( list( r.smembers(CLIENT_KEY) ) )
			s.sendto(cls, addr)
		print "Stats response sent to %s:%s" % addr

def handleClient(c, addr):
	g = gb.GameProtocolServer(c)
	# grab packet generator
	packets = g.waitForPacket()
	# get first init packet
	p = packets.next()
	cl = g.addClient(p)
	#send first response w/ raw game data, or error if invalid initialization packet
	resp = {}
	if not cl:
		resp['ErrerID'] = -1
		g.sendResponse(resp)
		return
	else:
		resp['ErrorID'] = 0
		if cl['Type'] == 'Player':
			resp['Data'] = emptyGameData
		g.sendResponse(resp)
	
	print "Added client %s." % cl['ID']
	
	if cl['Type'] == 'Player':
		for p in packets:
			# receive packet
			err = 0
			# forward to any viewers with error id
			if 'Data' in p:
				print "Update from %s, broadcasting to %d viewers." % ( cl['ID'], g.broadcastToViewers(cl, p['Data']) )
			else:
				err = -1
			# make response, right now we don't error check user's game
			resp = {"ErrorID": err}
			g.sendResponse(resp)
	else:
		for p in g.getViewerUpdate(cl):
			resp = {"Data": p}
			g.sendResponse(resp)
	g.removeClient(cl)
	print "User %s has left." % cl['ID']
	c.close()


# Start stats server

Process(target=statsServer).start()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)


i = 0
while 1:
	i += 1
	(c, addr) = s.accept()
	Process(target=handleClient, args=(c, addr)).start()
	print "Starting #%s process for client, pid is %s" % (i, os.getpid())


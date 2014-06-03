import gameprotocol as gb
import socket
from multiprocessing import Process
import os
import redis
import json


chessBoard = [	[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0] ]
emptyGameData = json.dumps(chessBoard)
print emptyGameData

def handleClient(c, addr):
	print "Started client process"
	g = gb.GameProtocolServer(c)
	packets = g.waitForPacket()
	# get first init packet
	print "1"
	p = packets.next()
	print "2"
	print p
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
		
	print "Added client %s" % cl['ID']
	if cl['Type'] == 'Player':
		for p in packets:
			# receive packet
			err = 0
			print p
			# forward to any viewers with error id
			if 'Data' in p:
				print "Broadcast to %d viewers." % g.broadcastToViewers(cl, p['Data'])
			else:
				err = -1
			# make response, right now we don't error check user's game
			resp = {"ErrorID": err}
			g.sendResponse(resp)
	else:
		for p in g.getViewerUpdate(cl):
			resp = {"Data": p}
			g.sendResponse(resp)
	c.close()

TCP_IP = '127.0.0.1'
TCP_PORT = 5010



BUFFER_SIZE = 20  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)


i = 0
while 1:
	i += 1
	(c, addr) = s.accept()
	Process(target=handleClient, args=(c, addr)).start()
	print "%d: in par aft c fork, %s" % (i, os.getpid())


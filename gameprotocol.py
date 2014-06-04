import re
import socket
import redis
import time
import select

class GameProtocolServer:
	# expects tcp socket of server
	p = {}
	DEL = "\r\n"
	TCP_BUFFER_SIZE = 20
	DBG = 1
	
	def __init__(self, c):
		self.r = redis.Redis('localhost')
		self.c = c
		IDCounter = self.r.get("IDCounter")
		if not IDCounter:
			self.r.set("IDCounter", 0)
	# c -> socket connection
	# type -> ClientType: Player/Viewer
	# id -> gameid
	def addClient(self, p):
		cl = {}
		cType = p['ClientType']
		if cType in ('Player', 'Viewer'):
			self.r.incr("IDCounter")
			clientID = self.r.get("IDCounter")
			if self.DBG: print "serv: incrementing client ID, %s" % clientID
		else:
			return
		if cType == 'Player':
			# give new id
			cl['ID'] = clientID
			cl['Type'] = 'Player'
		elif cType == 'Viewer':
			if self.gameExists(p['GameID']):
				cl['ID'] = clientID
				cl['Type'] = 'Viewer'
				cl['Viewing'] = p['GameID']
				self.addViewer(cl)
			else:
				return None
		typeKey = ":".join( [cl['ID'], "Type"] )
		if self.DBG: print "serv: setting %s, %s" % (typeKey, cl['Type'])
		self.r.set(typeKey, cl['Type'])
		self.r.sadd("Clients", cl['ID'])
		return cl

	def removeClient(self, cl):
		clKey = ":".join( [cl['ID'], "Type"] )
		if self.DBG: print "serv: removing %s" % clKey
		self.r.delete(clKey)

	# called by viewer
	def addViewer(self, cl):
		gameID = cl['Viewing']
		viewersKey = ":".join( [gameID, "Viewers"] )
		self.r.sadd(viewersKey, cl['ID'])

	# called by player
	def getViewers(self, cl):
		gameID = cl['ID']
		viewersKey = ":".join( [gameID, "Viewers"] )
		return list( self.r.smembers(viewersKey) )
	
	def broadcastToViewers(self, cl, data):
		viewers = self.getViewers(cl)
		for viewer in viewers:
			viewerKey = ":".join( [viewer, "Data"] )
			self.r.lpush(viewerKey, data)
		return len(viewers)

	# this is iterable, returns updates as they come
	# sleeps for 10 ms currently between checking redis for updates
	def getViewerUpdate(self, cl):
		viewerKey = ":".join( [cl['ID'], "Data"] )
		while(1):
			data = self.r.rpop(viewerKey)
			if data:
				yield data
			time.sleep(0.01)

	def gameExists(self, gid):
		clients = self.r.smembers("Clients")
		return (gid in clients)
		
	def waitForPacket(self):
		s = self.c
		while(1):
			p = {}
			packet = ""
			data = s.recv(self.TCP_BUFFER_SIZE)
			# if connection is over, quit
			if not data:
				break
			# look for <start> tag
			elif(data[0:7] == "<start>"):
				packet += data[9:]
				#print packet
				while 1:
					m = re.search("(<end>)", packet)
					if m:
						end = m.start(1)
						packet = packet[:end].strip().split(self.DEL)
						break
					packet += s.recv(self.TCP_BUFFER_SIZE)
					if not data:
						break
					# is packet too large with no <end> in sight?
					if len(packet) > 5000:
						break
					#print packet
				# create the dictionary
				for x in packet:
					[a, b] = x.split(": ")
					p[a] = b
				yield p

	# sends packet, returns # of sent chars
	def sendResponse(self, dict):
		c = self.c
		packet = self.createPacket(dict)
		return c.send(packet)

	# expects dictionary, creates packet
	def createPacket(self, d):
		p = "<start>\r\n"
		for key, val in d.items():
			p += "%s: %s\r\n" % (key, val)
		p += "<end>\r\n"
		return p
			
class GameProtocolClient:
	# expects tcp socket of server
	p = {}
	DEL = "\r\n"
	TCP_BUFFER_SIZE = 20
	DBG = 1
	
	def __init__(self, c):
		self.c = c

	def startGame(self):
		if self.DBG: print "Starting game"
		p = {'ClientType': 'Player'}
		self.sendResponse(p)

	def viewGame(self, gameID):
		if self.DBG: print "Starting viewer game"
		p = {'ClientType': 'Viewer', 'GameID': str(gameID)}
		self.sendResponse(p)

	# sends packet, returns # of sent chars
	def sendResponse(self, dict):
		c = self.c
		packet = self.createPacket(dict)
		return c.send(packet)

	# expects dictionary, creates packet
	def createPacket(self, d):
		p = "<start>\r\n"
		for key, val in d.items():
			p += "%s: %s\r\n" % (key, val)
		p += "<end>\r\n"
		return p
	# timeout in ms
	def waitForPacket(self):
		s = self.c
		while(1):
			p = {}
			packet = ""
			data = s.recv(self.TCP_BUFFER_SIZE)
			# if connection is over, quit
			if not data:
				break
			# look for <start> tag
			elif(data[0:7] == "<start>"):
				packet += data[9:]
				while 1:
					m = re.search("(<end>)", packet)
					if m:
						end = m.start(1)
						packet = packet[:end].strip().split(self.DEL)
						break
					packet += s.recv(self.TCP_BUFFER_SIZE)
					if not data:
						break
					# is packet too large with no <end> in sight?
					if len(packet) > 5000:
						break
				# create the dictionary
				for x in packet:
					a = ""
					b = ""
					# To save us from colons in JSON packing
					if x[0:6] == "Data: ":
						a = "Data"
						b = x[6:]
					else:
						[a, b] = x.split(": ")
					p[a] = b
				yield p
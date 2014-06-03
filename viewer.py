
import socket
from time import sleep
import gameprotocol as gb
import json
import sys
import curses

TCP_IP = '127.0.0.1'
TCP_PORT = 5010
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response
MESSAGE = "Hello, World!"


def startPlayer(ip, port):
	c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	c.connect( (ip, port) )
	print "Started client process"
	g = gb.GameProtocolClient(c)
	packets = g.waitForPacket()
	g.viewGame("47")
	p = packets.next()
	if p['ErrorID'] == "0":
		for p in packets:
			chessBoard = json.loads( p['Data'] )
			print chessBoard
	c.close()

def drawBoard(board):
	out = []
	s = ""
	i = 0
	for row in board:
		if i == 0: out.append(" _ _ _ _ _ _ _ _ ")
		j = 0
		s = ""
		for col in row:
			s += "|"
			if col:
				s += "x"
			else:
				s += "_"
			j += 1
		s += "|"
		out.append(s)
		i += 1
	return out

def knightPos(bx, by, kx, ky):
	x = 1 + bx + (kx * 2)
	y = 1 + by + ky
	return [y, x]

def previousMove(kx, ky):
	if chessBoard[ky][kx]:
		return True
	else:
		return False
def validMove(kx, ky, kx_last, ky_last):
	if not previousMove(kx, ky):
		xd = abs(kx - kx_last)
		yd = abs(ky - ky_last)
		if (xd + yd) == 3 and xd != 3 and yd != 3:
			return True
		else:
			return False


TCP_IP = '127.0.0.1'
TCP_PORT = 5010
BUFFER_SIZE = 1024

myscr = curses.initscr()

curses.noecho()
curses.cbreak()
curses.curs_set(0)
myscr.timeout(10)
myscr.keypad(1)

# board position
by, bx = [12, 25]
# cursor position
ky = 0
kx = 0
# last move position
ky_last = ky
kx_last = kx

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect( (TCP_IP, TCP_PORT) )
print "Started client process"
g = gb.GameProtocolClient(c)
packets = g.waitForPacket()
g.viewGame("60")
p = packets.next()
if p['ErrorID'] != "0":
	sys.exit(1)

while 1:
	myscr.refresh()
	c = myscr.getch()
	if c == ord('q'):
		break
	myscr.clear()
	i = 0
	p = packets.next()
	chessBoard = json.loads( p['Data'] )
	for row in drawBoard(chessBoard):
		myscr.addstr( by + i,  bx, row )
		i += 1
	[y, x] = knightPos(bx, by, kx_last, ky_last)
	myscr.addstr( y, x, "O" )
	[y, x] = knightPos(bx, by, kx, ky)
	myscr.addstr( y, x, "k" )

c.close()

curses.nocbreak()
curses.curs_set(1)
myscr.keypad(0)
curses.echo()

curses.endwin()
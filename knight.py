import curses


chessBoard = [	[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0],	\
				[0,0,0,0,0,0,0,0] ]

cursorLetter = "/"
placeLetter = "O"

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


myscr = curses.initscr()

curses.noecho()
curses.cbreak()
curses.curs_set(0)
myscr.keypad(1)

# board position
by, bx = [12, 25]
# cursor position
ky = 0
kx = 0
# last move position
ky_last = ky
kx_last = kx
# fill starting space
chessBoard[ky][kx] = 1
i = 0
for row in drawBoard(chessBoard):
	myscr.addstr( by + i,  bx, row )
	i += 1
[y, x] = knightPos(bx, by, kx, ky)
myscr.addstr( y, x, cursorLetter )
myscr.refresh()

while 1:
	myscr.refresh()
	c = myscr.getch()
	if c == curses.KEY_UP:
		if ky > 0:
			ky -= 1
	if c == curses.KEY_DOWN:
		if ky < 7:
			ky += 1
	if c == curses.KEY_LEFT:
		if kx > 0:
			kx -= 1
	if c == curses.KEY_RIGHT:
		if kx < 7:
			kx += 1
	if c == ord('u'):
		if validMove(kx, ky, kx_last, ky_last):
			ky_last = ky
			kx_last = kx
			chessBoard[ky][kx] = 1
	elif c == ord('q'):
		break
	myscr.clear()
	i = 0
	for row in drawBoard(chessBoard):
		myscr.addstr( by + i,  bx, row )
		i += 1
	[y, x] = knightPos(bx, by, kx_last, ky_last)
	myscr.addstr( y, x, placeLetter)
	[y, x] = knightPos(bx, by, kx, ky)
	myscr.addstr( y, x, cursorLetter )

curses.nocbreak()
curses.curs_set(1)
myscr.keypad(0)
curses.echo()

curses.endwin()

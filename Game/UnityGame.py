#coding:utf-8
__author__ = 'ear_breakfast'

from AI.Agent import Agent
import socket
import threading

# 将获取的字符串转为棋盘
def strToBoard(recStr):
	if recStr is None or len(recStr) == 0:
		print "empty or null."

	strArray = recStr.strip('\r\n').split('\n')
	for i in range(len(strArray)):
		eachChar = strArray[i].split(' ')
		for j in range(len(eachChar)):
			tmp = int(eachChar[j])
			if tmp == 1:
				board[i][j] = 1
			elif tmp == 2:
				board[i][j] = 2
			else:
				board[i][j] = 0

# 将获取的棋盘转为字符串
def boardToStr(board):
	if board is None or len(board) == 0:
		return ''
	sendStr = ''
	for i in range(AIrobot.state.rows):
		sendStr += ' '.join(str(board[i][x]) for x in range(AIrobot.state.cols))
		# sendStr += ' '.join(str(board[i][x].value) for x in range(AIrobot.state.cols))
		sendStr += '\n'
	print sendStr
	return sendStr


AIrobot = Agent()
AIrobot.threshold = 0.
board = [[0] * 7 for _ in range(6)]

sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.bind(("127.0.0.1",8080))
sk.listen(5)

print "waiting for connection..."
def tcplink(conn, addr):
	print "Accept new connection from %s:%s" % addr
	# conn.send("Welcome to ConnectFour Game!")
	while True:
		rec = conn.recv(512)
		print "receive..."
		print rec
		if rec == 'exit' or not rec:
			break
		strToBoard(rec)
		AIrobot.state.turn = 1
		newBoard = AIrobot.move(board)
		conn.send(boardToStr(newBoard))
		print "send already..."

	conn.close()
	print "Connection from %s:%s closed." % addr

while True:
	conn, addr = sk.accept()
	th = threading.Thread(target=tcplink, args=(conn, addr))
	th.start()


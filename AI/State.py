#coding:utf-8
__author__ = 'ear_breakfast'

class State(object):
	def __init__(self):
		self.board = [[0] * 7 for _ in range(6)]
		self.turn = 1
		self.moves = []
		self.rows = 6
		self.cols = 7


	def printBoard(self):
		"""Print the board."""
		for i in range(self.rows):
			print '  '.join(str(self.board[i][x]) for x in range(self.cols))
			# print '  '.join(str(self.board[i][x].value) for x in range(self.cols))

	def get_value(self, r, c):
		return self.board[r][c]

	def get_column(self, col):
		return [self.board[row][col] for row in range(0, 6)]

	def get_row(self, row):
		return self.board[row]

	def BoardValue(self, row, col):
		if (row >= 0 and row <= self.rows - 1 and col >= 0 and col <= self.cols - 1):
			return self.board[row][col]
		return -1

	# 递归检测周边与自己相同的棋子的数目
	def GetAdj(self, row, col, row_inc, col_inc):
		if (self.BoardValue(row, col) == self.BoardValue(row + row_inc, col + col_inc)
		    and self.BoardValue(row, col) != -1 and self.BoardValue(row + row_inc, col + col_inc) != -1
		    and self.BoardValue(row, col) != 0 and self.BoardValue(row + row_inc, col + col_inc) != 0):
			return 1 + self.GetAdj(row + row_inc, col + col_inc, row_inc, col_inc)
		else:
			return 0

	# 判断是否平局
	def isTie(self):
		for i in range(self.rows):
			for j in range(self.cols):
				if (self.board[i][j] == 0):
					return False
		return True

	# 找到指定列上第一个非空行的索引
	def lastRow(self, col):
		row = -1
		for i in range(self.rows):
			if self.board[i][col] != 0:
				row = i
				break
		return row

	# 判断是否胜利
	def isWin(self, row, col):
		# 水平方向
		if (self.GetAdj(row, col, 0, -1) + self.GetAdj(row, col, 0, 1) > 2):
			return True
		else:
			# 垂直方向
			if (self.GetAdj(row, col, 1, 0) > 2):
				return True
			else:
				# 左下角和右上角
				if (self.GetAdj(row, col, 1, -1) + self.GetAdj(row, col, -1, 1) > 2):
					return True
				else:
					# 右下角和左上角
					if (self.GetAdj(row, col, -1, -1) + self.GetAdj(row, col, 1, 1) > 2):
						return True
					else:
						return False

	# 判断游戏是否结束
	def isGameOver(self, col, test=False):
		row = self.lastRow(col)
		win = self.isWin(row, col)
		tie = self.isTie()
		if win or tie:
			if not test:
				print "GameOver!!!!"
				if win:
					print "White Wins!" if self.turn == 1 else "Black Wins!"
				else:
					if tie:
						print "DRAW!"

			return True
		return False


	# 放置棋子
	def insert_disc(self, col):
		column = self.get_column(col)
		if column[0] != 0:
			return "error"

		insert_idx = 5 - column[::-1].index(0)
		self.board[insert_idx][col] = self.turn
		self.moves.append([insert_idx, col])
		self.turn = 1 if self.turn == 2 else 2

	# 撤销操作
	def undo_move(self):
		last_move = self.moves.pop()
		self.board[last_move[0]][last_move[1]] = 0
		self.turn = 1 if self.turn == 2 else 2

	# 找到可插入的位置
	def possible_insertions(self):
		row = 0
		possible = []
		while len(possible) == 0 and row < self.rows:
			for col in range(7):
				if self.board[row][col] == 0:
					possible.append(col)
			row += 1

		return possible

	# 压缩棋盘状态
	def bitPack(self):
		"""
		First 126 bits encode value at each of 42 cells
		Last bit encodes whose turn it is
		"""
		bit = 0
		counter = 0
		n_bit_per_pos = 3
		for row in self.board:
			for ele in row:
				if ele == 0:
					bit += 1 * 2 ** (n_bit_per_pos * counter)
				if ele == 1:
					bit += 2 * 2 ** (n_bit_per_pos * counter)
				if ele == 2:
					bit += 4 * 2 ** (n_bit_per_pos * counter)
				counter += 1
		if self.turn == 1:
			bit += 1 * 2 ** (n_bit_per_pos * 42)
		return bit

	# 解压缩出棋盘和当前玩家
	def bitUnpack(self, bit):
		n_bit_per_pos = 3
		on_bit_pos = []
		bit_copy = bit % (2 ** (n_bit_per_pos * 42))

		if bit_copy < bit:  # largest bit = 1
			turn = 1
		else:
			turn = 2

		while bit_copy > 0:
			p = bit_copy.bit_length() - 1
			on_bit_pos.append(p)
			bit_copy -= 2 ** p
		all_values = [0 for _ in range(42)]

		for bit_pos in on_bit_pos:
			pos = int(bit_pos / 3)
			if bit_pos % 3 == 1:
				all_values[pos] = 1
			elif bit_pos % 3 == 2:
				all_values[pos] = 2
		board = []
		for i in range(0, len(all_values), 6):
			board.append(all_values[i:(i + 6)])
		return board, turn

#coding:utf-8
__author__ = 'ear_breakfast'

from State import State
import random
import os
import pickle
from collections import defaultdict

class Agent(object):
	def __init__(self, is_black=True, q_file_path="q_values"):
		# 棋盘状态初始化
		self.state = State()
		self.state.turn = 1 if is_black == True else 2

		# Q table初始化
		self.Q = None
		if os.path.exists(q_file_path) and os.path.isfile(q_file_path):
			with open(q_file_path, 'r') as f:
				print "loading Q-table..."
				self.Q = pickle.load(f)
		else:
			print "initial Q-table..."
			self.Q = defaultdict(float)

		# 参数
		self.threshold = 0.1
		self.gamma = 0.9
		self.alpha = 0.1
		self.reward = 1.

	# agent落子
	def move(self, inp):
		self.state.board = inp
		r = random.random()
		if r < self.threshold:
			move = self.random_move()
		else:
			move = self.move_by_rl()
		return move

	# 指定列的走步
	def apply_move(self, move):
		self.state.insert_disc(move)
		self.last_move = move

	# 随机落子
	def random_move(self):
		possible_col = self.state.possible_insertions()
		col_indices = random.choice(possible_col)
		self.apply_move(col_indices)
		return self.state.board

	# 根据Q-table贪婪落子
	def move_by_rl(self):
		action = self.next_action()
		self.apply_move(action)
		return self.state.board

	def next_action(self):
		possible = self.state.possible_insertions()
		if len(possible) == 0:
			return None

		# 查看是否能一步后直接胜利or平局
		for action in possible:
			self.state.insert_disc(action)
			winner = self.state.isGameOver(action, test=True)
			self.state.undo_move()
			if winner:
				return action

		# 返回Q值最大的落子列
		action_list = []
		max_common_bits = 0
		cur_turn = self.state.turn
		bitpacked_state = self.state.bitPack()

		for state_move, q_value in self.Q.items():
			if self.state.bitUnpack(state_move[0])[1] != cur_turn:
				continue
			num_common_bits = bin(bitpacked_state ^ state_move[0]).count("1")
			if num_common_bits > max_common_bits:
				max_common_bits = num_common_bits
				action_list = [(state_move[1], q_value)]
			if num_common_bits == max_common_bits:
				action_list.append((state_move[1], q_value))

		action_list.sort(key=lambda x: x[1], reverse=True)
		for action in action_list:
			if action[0] in possible:
				return action[0]

		return random.choice(possible)


	# 训练
	def train(self):
		trace = []
		black_agent = Agent()
		white_agent = Agent()

		while True:
			cur_state = white_agent.state.bitPack()
			turn = white_agent.state.turn

			if turn == 1:
				black_agent.move(black_agent.state.board)
				move = black_agent.last_move

				if move is None:
					return
				white_agent.apply_move(move)
			else:
				white_agent.move(white_agent.state.board)
				move = white_agent.last_move
				if move is None:
					return
				black_agent.apply_move(move)

			# 保存落子轨迹
			trace.append((cur_state, move))
			gameover = white_agent.state.isGameOver(move)

			if gameover:
				self.update_qtable(trace, turn, black_agent, white_agent)
				white_agent.state.printBoard()
				break

	# 更新Q-table
	def update_qtable(self, trace, winner, black_agent, white_agent):
		# 根据赢家获取两个player的反向move list
		if winner == 2:
			sign = 1.
			white_moves = trace[::-2]
			black_moves = trace[:-1][::-2]
		else:
			sign = -1.
			black_moves = trace[::-2]
			white_moves = trace[:-1][::-2]

		self.update(sign, white_moves)
		self.update(-1*sign, black_moves)


	def update(self, sign, moves):
		last = moves[0]
		for move in moves:
			self.Q[move] += self.alpha * (sign*self.reward + self.gamma * self.Q[last] - self.Q[move])
			last = move


	def save(self, f):
		pickle.dump(self.Q, f)
		print "q-table saved."

if __name__ == "__main__":
	NUM_GAMES = 30000
	FILE = "q_values"
	agent = Agent(is_black=True, q_file_path=FILE)

	for i in range(NUM_GAMES):
		print "trainning epoches: ", i
		agent.train()
		agent.state = State()

	with open(FILE, 'w') as f:
		agent.save(f)

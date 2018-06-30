#coding:utf-8
__author__ = 'ear_breakfast'

from AI.Agent import Agent
import random

# 人机对弈
turn = random.randint(1,2)
print "先手棋子颜色: ", turn
is_black = True if turn == 1 else False
robot = Agent(is_black=is_black)
# 设置为完全贪婪模式,无随机走步
robot.threshold = 0.

while True:
	# robot先走
	robot.move(robot.state.board)
	robot.state.printBoard()
	if robot.state.isGameOver(robot.last_move):
		robot.state.printBoard()
		break

	# human后走
	col = input('your turn: ')
	robot.apply_move(int(col))
	if robot.state.isGameOver(col):
		robot.state.printBoard()
		break



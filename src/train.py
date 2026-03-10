from board import Board
from display import Display


from agent import Agent


board = Board((10, 10))
agent = Agent.load("src/brain.json")
display = Display(board, agent, 1)
display.run()

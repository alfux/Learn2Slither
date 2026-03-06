from board import Board
from display import Display


from agent import Agent


board = Board()
agent = Agent.load("brain.json")
display = Display(board, agent, 1)
display.run()

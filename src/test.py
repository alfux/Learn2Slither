from board import Board
from display import Display


from agent import Agent


board = Board((10, 10))
agent = Agent.load("agent.json", training=False)
display = Display(board, agent, 0)
display.run()

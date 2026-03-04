from board import Board
from display import Display

from alfux.mlp import MLP


from agent import Agent


mlp = MLP.loadf("brain.json")
board = Board()
agent = Agent(board, mlp)
display = Display(agent)
display.run()

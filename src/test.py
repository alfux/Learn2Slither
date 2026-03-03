from board import Board
from display import Display

from alfux.mlp import MLP


from agent import Agent


mlp = MLP.loadf("brain.json")
board = Board((20, 20))
print(board)
agent = Agent(board, mlp)
display = Display(agent)
display.run()

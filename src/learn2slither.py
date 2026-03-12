"""Main module of the application"""

from typing import Self

from agent import Agent
from board import Board
from display import Display
from interpreter import Interpreter


class Learn2Slither:
    """Main program class"""

    def __init__(self: Self, **parameters: dict) -> None:
        """Instanciate an instance of Learn2Slither.

        KWArgs:
            parameters (dict): Application parameters.
        """
        self._agent = Agent.load(parameters["agent"])
        self._board = Board(parameters.get("board_size", None))
        self._display = Display(*self._board.shape, self.update)
        self._interpreter = Interpreter(-1, 1, -0.25, -0.01)
        self._running_app = False
        self._play = False
        self._sessions = parameters["sessions"]
        self._iteration = 0

    def run(self: Self) -> None:
        """Run the main loop."""
        self._display.run()
        self._agent.save("agent.json")

    def update(self: Self) -> None:
        """Train with display."""
        move = self._agent.play(self._interpreter, self._board)
        item = self._board.move(move)
        self._interpreter.interpret(item)
        self._agent.learn(self._interpreter, self._board)
        if not self._interpreter.snake_alive:
            self._iteration += 1
            print("death", self._iteration)
            self._board = Board(self._board.shape)
            if self._iteration >= self._sessions:
                self._display.close()
        return self._board.state

    def _background_train(self: Self) -> None:
        """Train without display."""
        pass

"""Main module of the application"""

from typing import Self

from agent import Agent
from board import Board
from interpreter import Interpreter


class Learn2Slither:
    """Main program class"""

    def __init__(self: Self, **parameters: dict) -> None:
        """Instanciate an instance of Learn2Slither.

        KWArgs:
            parameters (dict): Application parameters.
        """
        self._agent = Agent.load(
            parameters["agent"],
            learning=(not parameters.get("no_learn", False))
        )
        self._board = Board(parameters.get("board_size", None))
        self._interpreter = Interpreter(self._board, -1, 1, -0.25, 0)
        self._running_app = False
        self._play = False
        self._sessions = parameters["sessions"]
        self._iteration = 0

    @property
    def agent(self: Self) -> Agent:
        """Get the agent.

        Returns:
            Agent: The agent.
        """
        return self._agent

    @property
    def board(self: Self) -> Board:
        """Get the current board.

        Returns:
            Board: The current board.
        """
        return self._board

    @property
    def interpreter(self: Self) -> Interpreter:
        """Get the interpreter.

        Returns:
            Interpreter: The interpreter.
        """
        return self._interpreter

    def update(self: Self) -> bool:
        """Plays and train.

        Returns:
            bool: True when the session is over.
        """
        if self._interpreter.snake_alive:
            move = self._agent.play(self._interpreter, self._board)
            self._interpreter.add_move(move)
            item = self._board.move(move)
            self._interpreter.interpret(item)
            self._agent.learn(self._interpreter, self._board)
        else:
            self._board = Board(self._board.size)
            self._interpreter.board = self._board
            self._iteration += 1
            if self._iteration >= self._sessions:
                return True
        return False

    def train(self: Self) -> None:
        """Trains the model in a single loop, without any kind of display."""
        while not self.update():
            pass

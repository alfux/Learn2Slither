"""Agent module contains the player AI."""

from typing import Self

from alfux.mlp import MLP

from board import Board


class Agent:
    """Learn and plays the game."""

    def __init__(self: Self, mlp: MLP = None) -> None:
        """Instanciate the Agent.

        Args:
            mlp (MLP): Optional neural network to use.
        """
        self._mlp = mlp

    def play(self: Self, board: Board) -> None:
        """Execute a move in the board.

        Args:
            board: The game board.
        """
        pass

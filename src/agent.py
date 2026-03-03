"""Agent module contains the player AI."""

from typing import Self

import numpy as np
from alfux.mlp import MLP

from board import Board


class Agent:
    """Learn and plays the game."""

    def __init__(self: Self, board: Board, mlp: MLP) -> None:
        """Instanciate the Agent.

        Args:
            mlp (MLP): Neural network.
        """
        self._board = board
        self._mlp = mlp
        self._last_context = None

    @property
    def board(self: Self) -> Board:
        """Get the board.

        Returns:
            Board: The board.
        """
        return self._board

    @board.setter
    def board(self: Self, value: Board) -> None:
        """Set the board.

        Args:
            value (Board): The new board.
        """
        self._board = value

    def play(self: Self) -> int:
        """Execute a move in the board.

        Returns:
            int: The item on the board after a move.
        """
        view = np.atleast_2d(np.concatenate(self._board.view()))
        higher_reward = -np.inf
        for i in range(4):
            context = np.concatenate((view, [[i]]), axis=1)
            reward = self._mlp.eval(context)
            if reward > higher_reward:
                self._last_context = context
                higher_reward = reward
        match self._last_context[0, -1]:
            case 0:
                return self._board.up()
            case 1:
                return self._board.down()
            case 2:
                return self._board.left()
            case 3:
                return self._board.right()

    def learn(self: Self, reward: float) -> None:
        """Learn from success or mistake represented by reward.

        Args:
            reward (float): Success or mistake indicator.
        """
        self._mlp.update(np.array([[reward]]), self._last_context)

"""Interpreter managing rewards and interpretations of states and actions."""

from collections import deque
from typing import Self

import numpy as np
from numpy import ndarray

from board import Board


class Interpreter:
    """Manage rewards and interpretations of states and actions."""

    def __init__(
            self: Self,
            board: Board,
            death_reward: float,
            green_reward: float,
            red_reward: float,
            neutral_reward: float
    ) -> None:
        """Instanciate an interpreter.

        Args:
            death_reward (float): reward for death.
            green_reward (float): reward for green apple.
            red_reward (float): reward for red apple.
            neutral_reward (float): reward for neutral move.
        """
        self._rules = {
            Board.W: [death_reward, False],
            Board.S: [death_reward, False],
            Board.G: [green_reward, True],
            Board.R: [red_reward, True],
            Board.N: [neutral_reward, True],
            -1: [death_reward, False]
        }
        self.board = board

    @property
    def board(self: Board) -> Board:
        """Get current board.

        Returns:
            Board: Current board.
        """
        return self._board

    @board.setter
    def board(self: Self, value: Board) -> None:
        """Set the board.

        Args:
            value (Board): The new board.
        """
        self._actions = deque([''] * (value.shape[0] + 2))
        self._board = value
        self._is_alive = True
        self._last_item = Board.H
        self._reward = 0

    @property
    def item(self: Self) -> int:
        """Get the last received item.

        Returns:
            int: The last received item.
        """
        return self._last_item

    @property
    def reward(self: Self) -> float:
        """Get the last interpreted reward.

        Returns:
            float: The last interpreted reward.
        """
        return self._reward

    @property
    def snake_alive(self: Self) -> bool:
        """Get the last interpreted snake's state.

        Returns:
            bool: The last interpreted snake's state.
        """
        return self._is_alive

    def interpret(self: Self, item: int) -> None:
        """Interpret item's reward and state of the snake.

        Args:
            item (int): Kind of item the snake stepped on.
        """
        self._reward, self._is_alive = self._rules[item]
        self._last_item = item

    def add_move(self: Self, move: int) -> None:
        """Add a move in the last moves list.

        Args:
            move (int): The move code.
        """
        self._actions.appendleft(Board.MOVES[move])
        self._actions.pop()

    def terminal_display(self: Self) -> None:
        """Print the terminal display."""
        n, m = self._board.head
        view = np.zeros(self._board.shape + np.array([2, 2])).astype(str)
        view[:, :] = " "
        view[:, m] = [Board.TOKEN[elem] for elem in self._board.state[:, m]]
        view[n, :] = [Board.TOKEN[elem] for elem in self._board.state[n, :]]
        string = [
            "\033[K" + ''.join(r) + '\t' + a
            for r, a in zip(view, self._actions)
        ]
        print("\n".join(string) + "\033[A" * (len(string) - 1) + '\r', end='')

    def clear_terminal_display(self: Self) -> None:
        """Clear the terminal display."""
        length = self._board.state.shape[0]
        print("\033[K\n" * length + "\033[A" * length, end="")

    @staticmethod
    def state(board: Board) -> tuple[ndarray, ndarray]:
        """Get the snake's view interpretation from the board.

        Args:
            board (Board): The environment.
        Returns:
            ndarray: An encoded interpretation of the view.
        """
        left = board.state[board.head[0], :board.head[1]]
        left = Interpreter._encode_axis(left, False)
        right = board.state[board.head[0], board.head[1] + 1:]
        right = Interpreter._encode_axis(right, True)
        up = board.state[:board.head[0], board.head[1]]
        up = Interpreter._encode_axis(up, False)
        down = board.state[board.head[0] + 1:, board.head[1]]
        down = Interpreter._encode_axis(down, True)
        return np.concatenate([left, right, up, down])

    @staticmethod
    def _encode_axis(direction: ndarray, symetry: bool) -> ndarray:
        """Encode a vision direction:

            distance_to_wall,
            distance_to_body,
            distance_to_poison,
            distance_to_reward

        Args:
            direction (ndarray): an ray of vision.
            symetry (bool): True to count distance from end of array.
        Returns:
            ndarray: encoded vision.
        """
        encoded = np.zeros(4)
        if symetry:
            direction = direction[::-1]
        for i, item in enumerate(direction):
            if item == Board.W:
                encoded[0] = int(1 == (len(direction) - i))
            elif item == Board.S:
                encoded[1] = 1 / (len(direction) - i)
            elif item == Board.R:
                encoded[2] = int(1 == (len(direction) - i))
            elif item == Board.G:
                encoded[3] = 1 / (len(direction) - i)
        return encoded

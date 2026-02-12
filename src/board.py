"""Board game module implementing the environment."""

from collections import deque
from typing import Self

import numpy as np
from numpy import ndarray


class Board:
    """Board class representing the environnement."""

    W, H, S, G, R = 1, 2, 3, 4, 5
    _TOKEN = dict({'W': 1, 'H': 2, 'S': 3, 'G': 4, 'R': 5})
    _ROTATION_R = np.array([[0, 1], [-1, 0]])
    _ROTATION_L = np.array([[0, -1], [1, 0]])

    def __init__(self: Self, shape: tuple = None) -> None:
        """Board instanciation.

        Args:
            shape (tuple): Dimension of the board.
        """
        self._shape = np.array(shape or (10, 10)) + np.array([1, 1])
        self._board = np.zeros(self._shape)
        self._board[0] = self.W
        self._board[-1] = self.W
        self._board[:, 0] = self.W
        self._board[:, -1] = self.W
        self._free_cells = list(np.argwhere(self._board == 0))
        self._create_snake()
        self._put_item_rand(self.G)
        self._put_item_rand(self.G)
        self._put_item_rand(self.R)

    def __str__(self: Self) -> str:
        """String representation of the board.

        Returns:
            str: String representation of the board.
        """
        board = str(self._board.astype(int))
        for key, value in self._TOKEN.items():
            board = board.replace(str(value), key)
        return board.replace('0', ' ')

    @property
    def state(self: Self) -> ndarray:
        """Get the state of the board.

        Returns:
            ndarray: The board matrix."""
        return self._board

    def forward(self: Self) -> int:
        """Move the snake one cell forward.

        Returns:
            int: The previous code of the head's new cell.
        """
        return self._move_snake(self._snake_dir)

    def right(self: Self) -> int:
        """Move the snake one cell to its right.

        Returns:
            int: The previous code of the head's new cell.
        """
        self._snake_dir = self._ROTATION_R @ self._snake_dir
        return self._move_snake(self._snake_dir)

    def left(self: Self) -> int:
        """Move the snake one cell up.

        Returns:
            int: The previous code of the head's new cell.
        """
        self._snake_dir = self._ROTATION_L @ self._snake_dir
        return self._move_snake(self._snake_dir)

    def view(self: Self) -> tuple[ndarray, ndarray]:
        """Get vertical and horizontal view of the snake."""
        vertical = self._board[:, self._snake[0][1]]
        horizontal = self._board[self._snake[0][0], :]
        return [vertical, horizontal]

    def _put_item_rand(self: Self, item: int) -> ndarray:
        """Put an item in a random free cell in the board.

        Args:
            item (int): Item code.
        Returns:
            ndarray: The random position of the item.
        """
        pos = self._free_cells.pop(np.random.randint(0, len(self._free_cells)))
        self._board[pos[0], pos[1]] = item
        return pos

    def _create_snake(self: Self) -> None:
        """Put the snake in a random free position in the board."""
        v, h = np.array([1, 0]), np.array([0, 1])
        hpos = self._put_item_rand(self.H)
        self._snake = deque([tuple(hpos)])
        around = [hpos + v, hpos - v, hpos + h, hpos - h]
        free = [cell for cell in around if self._board[cell[0], cell[1]] == 0]
        pos = tuple(free[np.random.randint(0, len(free))])
        self._snake_dir = hpos - pos
        self._board[pos] = self.S
        self._snake.append(pos)
        around = [pos + v, pos - v, pos + h, pos - h]
        free = [cell for cell in around if self._board[cell[0], cell[1]] == 0]
        pos = tuple(free[np.random.randint(0, len(free))])
        self._board[pos] = self.S
        self._snake.append(pos)

    def _move_snake(self: Self, dir: ndarray) -> int:
        """Move the snake of one cell in a direction.

        Args:
            dir (ndarray): normed direction of the movement.
        Returns:
            int: The previous code of the head's new cell.
        """
        pos = tuple(self._snake[0] + dir)
        last_item = self._board[pos]
        self._board[self._snake[0]] = self.S
        self._board[pos] = self.H
        self._snake.appendleft(pos)
        match last_item:
            case self.W:
                self._board[self._snake.pop()] = 0
                self._snake_dir = np.zeros(2).astype(int)
            case self.S:
                self._board[self._snake.pop()] = 0
                self._snake_dir = np.zeros(2).astype(int)
            case self.R:
                self._board[self._snake.pop()] = 0
                self._board[self._snake.pop()] = 0
            case 0:
                self._board[self._snake.pop()] = 0
        if len(self._snake) == 0:
            return -1
        return last_item

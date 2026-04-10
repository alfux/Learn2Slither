"""Board game module implementing the environment."""

from bidict import bidict
from collections import deque
from typing import Self

import numpy as np
from numpy import ndarray


class Board:
    """Represent the environnement."""

    N, W, H, S, G, R = 0, 1, 2, 3, 4, 5
    TOKEN = dict({0: "0", 1: "W", 2: "H", 3: "S", 4: "G", 5: "R"})
    DIRECTIONS = np.array([[-1, 0], [1, 0], [0, -1], [0, 1]])
    MOVES = ["UP", "DOWN", "LEFT", "RIGHT"]

    def __init__(self: Self, size: int = None) -> None:
        """Board instanciation.

        Args:
            size (int): Dimension of the board.
        """
        if size is not None:
            size = np.clip(size, 3, None)
            self._shape = (size, size)
        else:
            self._shape = (10, 10)
        self._board = np.zeros(self._shape + np.array([2, 2]))
        self._board[0] = self.W
        self._board[-1] = self.W
        self._board[:, 0] = self.W
        self._board[:, -1] = self.W
        self._free_cell = np.argwhere(self._board == 0)
        self._free_cell = {k: tuple(v) for k, v in enumerate(self._free_cell)}
        self._free_cell = bidict(self._free_cell)
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
        for key, value in self.TOKEN.items():
            board = board.replace(str(key), value)
        return board

    @property
    def head(self: Self) -> tuple:
        """Get head coordinates.

        Returns:
            tuple: head row, head column.
        """
        return self._head

    @property
    def length(self: Self) -> int:
        """Get Snake's length.

        Returns:
            int: Snake's length.
        """
        return len(self._snake)

    @property
    def shape(self: Self) -> tuple:
        """Get the shape of the board.

        Returns:
            tuple: (height, width)
        """
        return self._shape

    @property
    def size(self: Self) -> int:
        """Get the size of the board.

        Returns:
            int: Length of one side of the square.
        """
        return self._shape[0]

    @property
    def state(self: Self) -> ndarray:
        """Get the state of the board.

        Returns:
            ndarray: The board matrix."""
        return self._board

    def move(self: Self, move: int) -> int:
        """Move th snake.

        Args:
            move: 0 UP, 1 DOWN, 2 LEFT, 3 RIGHT.
        Returns:
            int: The new cell's item.
        """
        return self._move_snake(self.DIRECTIONS[move])

    def _put_item_rand(self: Self, item: int) -> ndarray:
        """Put an item in a random free cell in the board.

        Args:
            item (int): Item code.
        Returns:
            ndarray: The random position of the item.
        """
        if len(self._free_cell) > 0:
            pos = self._pop_free(np.random.randint(0, len(self._free_cell)))
            self._board[pos[0], pos[1]] = item
            return pos
        return None

    def _remove_free(self: Self, pos: tuple) -> None:
        """Remove a free cell by position.

        Args:
            pos (tuple): matrix index to remove.
        """
        index = self._free_cell.inv[pos]
        last_i, last_pos = self._free_cell.popitem()
        if index != last_i:
            self._free_cell[index] = last_pos

    def _pop_free(self: Self, index: int) -> tuple:
        """Remove a free cell by index.

        Args:
            index (int): index of the cell in the list.
        Returns:
            tuple: the cell's position.
        """
        pos = self._free_cell[index]
        last_i, last_pos = self._free_cell.popitem()
        if index != last_i:
            self._free_cell[index] = last_pos
        return pos

    def _add_free(self: Self, pos: tuple) -> None:
        """Add a free cell.

        Args:
            pos (tuple): matrix index to add.
        """
        self._free_cell[len(self._free_cell)] = pos

    def _create_snake(self: Self) -> None:
        """Put the snake in a random free position in the board."""
        v, h = np.array([1, 0]), np.array([0, 1])
        hpos = self._put_item_rand(self.H)
        self._snake = deque([tuple(hpos)])
        self._head = hpos
        around = [hpos + v, hpos - v, hpos + h, hpos - h]
        free = [cell for cell in around if self._board[cell[0], cell[1]] == 0]
        pos = tuple(free[np.random.randint(0, len(free))])
        self._board[pos] = self.S
        self._snake.append(pos)
        self._remove_free(pos)
        around = [pos + v, pos - v, pos + h, pos - h]
        free = [cell for cell in around if self._board[cell[0], cell[1]] == 0]
        pos = tuple(free[np.random.randint(0, len(free))])
        self._board[pos] = self.S
        self._snake.append(pos)
        self._remove_free(pos)
        self._snake_alive = True

    def _move_snake(self: Self, dir: ndarray) -> int:
        """Move the snake of one cell in a direction.

        Args:
            dir (ndarray): normed direction of the movement.
        Returns:
            int: The previous code of the head's new cell.
        """
        if not self._snake_alive:
            return -1
        aim = tuple(self._snake[0] + dir)
        self._board[self._snake[0]] = self.S
        tail = self._cut_tail()
        item = self._put_head(aim)
        match item:
            case self.G:
                self._board[tail] = self.S
                self._snake.append(tail)
                self._remove_free(tail)
                self._put_item_rand(self.G)
            case self.R:
                self._cut_tail()
                if len(self._snake) == 0:
                    self._snake_alive = False
                    return -1
                self._put_item_rand(self.R)
            case 0:
                self._remove_free(aim)
            case _:
                self._snake_alive = False
        return item

    def _cut_tail(self: Self) -> tuple:
        """Remove the tip of the tail.

        Returns:
            tuple: The position of the tail's tip.
        """
        tail = self._snake.pop()
        self._board[tail] = 0
        self._add_free(tail)
        return tail

    def _put_head(self: Self, aim: tuple) -> int:
        """Put the head in aimed position.

        Returns:
            int: cell's item before the head.
        """
        item = self._board[aim]
        self._board[aim] = self.H
        self._snake.appendleft(aim)
        self._head = aim
        return item

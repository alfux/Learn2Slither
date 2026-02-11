"""Board game module implementing the environment."""

from typing import Self

import numpy as np
from bidict import bidict
from numpy import ndarray


class Board:
    """Board class representing the environnement."""

    TOKEN = bidict({0: 0, "W": 1, "H": 2, "S": 3, "G": 4, "R": 5})

    def __init__(self: Self, shape: tuple = None) -> None:
        """Board instanciation."""
        self._shape = np.array(shape or (10, 10)) + np.array([1, 1])
        self._board = self._new_board()

    def _new_board(self: Self) -> ndarray:
        """Set up a new board."""

    def _rand_pos(self: Self) -> ndarray:
        """Get a random free position in the board."""
        pass

    def _rand_snake(self: Self) -> ndarray:
        """"""
        pass

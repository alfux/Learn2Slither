"""Display module manages the graphic interface."""

import sys
from typing import Self

import numpy as np
import pyglet
from pyglet.graphics import Batch
from pyglet.image import SolidColorImagePattern, Texture
from pyglet.sprite import Sprite
from pyglet.window import key

from agent import Agent
from board import Board


class Display:
    """Manage the graphic interface."""

    def __init__(self: Self, board: Board, agent: Agent, temp: float) -> None:
        """Display instanciation

        Args:
            board (Board): The model board.
            agent (Agent): The player agent.
            temp (float): Temperature of the agent. High temperature means
                high randomness.
        """
        self._window = pyglet.window.Window()
        self._board, self._agent, self._temp = board, agent, temp
        self._last_distance = self._green_distance()
        self._stamina, self._max_stamina = 0, np.max(self._board.shape) ** 2
        self._tile_size = 32
        self._atlas = self._init_atlas()
        self._floor = self._atlas[0]
        self._wall = self._atlas[3]
        self._green_apple = self._atlas[2]
        self._red_apple = self._atlas[1]
        self._snake = self._atlas[4]
        self._head = self._atlas[5]
        self._height, self._width = board.state.shape
        self._batch = Batch()
        self._tiles = self._init_board_display()
        self._window.push_handlers(on_draw=self.on_draw)
        self._window.push_handlers(on_close=self.close)
        width = self._tile_size * self._width
        height = self._tile_size * self._height
        if sys.platform == "darwin":
            width /= 2
            height /= 2
        self._window.set_size(width, height)

    def run(self: Self) -> None:
        """Run the event loop."""
        pyglet.app.run()

    def close(self: Self) -> None:
        """Close the event loop."""
        self._agent.save("agent.json")
        pyglet.app.exit()

    def on_draw(self: Self) -> None:
        """Display event function."""
        self._window.clear()
        self._update_state()
        self._batch.draw()
        move = self._agent.play(self._board.view(), self._temp)
        cell = self._board.move(move)
        if not self._rules(cell):
            self._temp = np.max([0.05, self._temp - 1e-4])
            print(self._temp, end="                             ")

    def _rules(self: Self, cell: int) -> bool:
        """Apply rule of rewards.

        Args:
            cell (int): Kind of cell the snake stepped on.
        Returns:
            bool: True (alive), False (...dead).
        """
        view = self._board.view()
        match cell:
            case Board.W | Board.S | -1:
                return self._death_rules(view)
            case Board.G:
                return self._green_rules(view)
            case Board.R:
                return self._red_rules(view)
            case 0:
                return self._neutral_rules(view)
        raise ValueError("_rules: corrupted board cell.")

    def _death_rules(self: Self, view: tuple) -> bool:
        """Death rules.

        Args:
            view (tuple): current snake's view.
        Returns:
            bool: Returns False
        """
        self._agent.learn(view, -1, 0)
        self._board = Board(self._board.shape)
        self._last_distance = self._green_distance()
        self._stamina = self._max_stamina
        return False

    def _green_rules(self: Self, view: tuple) -> bool:
        """Green rules.

        Args:
            view (tuple): current snake's view.
        Returns:
            bool: Returns True
        """
        self._agent.learn(view, 1, 1)
        self._stamina = self._max_stamina
        return True

    def _red_rules(self: Self, view: tuple) -> bool:
        """Red rules.

        Args:
            view (tuple): current snake's view.
        Returns:
            bool: Returns True
        """
        self._agent.learn(view, -0.5, 1)
        self._stamina = self._max_stamina
        return True

    def _neutral_rules(self: Self, view) -> bool:
        """Red rules.

        Args:
            view (tuple): current snake's view.
        Returns:
            bool: True or False if the snake is alive or dead.
        """
        if self._stamina <= 0:
            return self._death_rules(view)
        new_distance = self._green_distance()
        delta = self._last_distance - new_distance
        delta = -0.01 if delta == 0 else 0.02 * np.sign(delta)
        self._agent.learn(view, delta, 1)
        self._last_distance = new_distance
        self._stamina -= 1
        return True

    def _green_distance(self: Self) -> int:
        """Distance to closest green.

        Returns:
            int: Distance to closest green.
        """
        distance = np.inf
        head = self._board.head
        for green in self._board.greens:
            d = green[0] - head[0] + green[1] - head[1]
            if d < distance:
                distance = d
        return distance

    def _init_board_display(self: Self) -> list[list[Sprite]]:
        """Initialize the board tiles.

        Returns:
            list[list[Sprite]]: A matrix of tiles.
        """
        n, m = self._board.state.shape
        offset = n - 1
        return [
            [
                Sprite(
                    self._floor,
                    self._tile_size * j,
                    self._tile_size * (offset - i),
                    batch=self._batch,
                )
                for j in range(m)
            ]
            for i in range(n)
        ]

    def _init_atlas(self: Self) -> list:
        """Initialize the texture atlas.

        Returns:
            list: TextureRegion to use for color swaps.
        """
        colors = [
            [100, 100, 100, 255],
            [200, 50, 50, 255],
            [50, 200, 50, 255],
            [50, 50, 50, 255],
            [50, 50, 200, 255],
            [50, 50, 100, 255],
        ]
        atlas = Texture.create(32 * len(colors), self._tile_size)
        for i, rgba in enumerate(colors):
            solid = SolidColorImagePattern(rgba)
            solid = solid.create_image(self._tile_size, self._tile_size)
            atlas.blit_into(solid, i * self._tile_size, 0, 0)
        return [
            atlas.get_region(
                i * self._tile_size, 0, self._tile_size, self._tile_size
            )
            for i in range(len(colors))
        ]

    def _update_state(self: Self) -> None:
        """Update the tile matrix to correspond to the board state."""
        for i in range(self._board.state.shape[0]):
            for j in range(self._board.state.shape[1]):
                match self._board.state[i, j]:
                    case Board.W:
                        self._tiles[i][j].image = self._wall
                    case Board.H:
                        self._tiles[i][j].image = self._head
                    case Board.S:
                        self._tiles[i][j].image = self._snake
                    case Board.G:
                        self._tiles[i][j].image = self._green_apple
                    case Board.R:
                        self._tiles[i][j].image = self._red_apple
                    case _:
                        self._tiles[i][j].image = self._floor

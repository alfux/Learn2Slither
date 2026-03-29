"""Display module manages the graphic interface."""

import sys
from typing import Self, Any

import numpy as np
import pyglet as pyg
import time
from numpy import ndarray
from pyglet.graphics import Batch
from pyglet.image import SolidColorImagePattern, Texture
from pyglet.sprite import Sprite
from pyglet.window import key

from board import Board
from learn2slither import Learn2Slither


class Display:
    """Manage the graphic interface."""

    def __init__(self: Self, app: Learn2Slither) -> None:
        """Display instanciation

        Args:
            update (Callable): function to call on display update.
            stop (Callable): function to call on close.
        """
        self._window = pyg.window.Window()
        self._tile_size = 32
        self._atlas = self._init_atlas()
        width, height = app.interpreter.board.shape
        self._width, self._height = width + 2, height + 2
        self._batch = Batch()
        self._tiles = self._init_board_display()
        self._window.on_draw = self.on_draw
        self._window.on_key_press = self.on_key_press
        self._window.on_close = self.on_close
        width = self._tile_size * self._width
        height = self._tile_size * self._height
        if sys.platform == "darwin":
            width /= 2
            height /= 2
        self._window.set_size(width, height)
        self._app = app
        self._sleep = 0
        self._last_time = time.time()
        self._step_by_step = False

    def run(self: Self) -> None:
        """Run the event loop."""
        pyg.app.run()

    def on_close(self: Self, _: Any = None) -> None:
        """Close the app.

        _ (Any): Unused parameter.
        """
        self._app.agent.save()
        self._app.interpreter.clear_terminal_display()
        self._window.close()

    def on_draw(self: Self) -> None:
        """Display event function."""
        self._window.clear()
        now = time.time()
        if not self._step_by_step and now - self._last_time > self._sleep:
            self._update_state(self._app.board.state)
            if self._app.update():
                pyg.clock.schedule_once(self.on_close, 0)
            self._last_time = now
        self._batch.draw()

    def on_key_press(self: Self, symbol: int, _: int) -> None:
        """Keyboard event function."""
        match symbol:
            case key.UP:
                self._sleep = np.clip(self._sleep - 0.05, 0, 1)
            case key.DOWN:
                self._sleep = np.clip(self._sleep + 0.05, 0, 1)
            case key.L:
                self._app.agent.learning = not self._app.agent.learning
            case key.P:
                self._step_by_step = not self._step_by_step
            case key.S:
                self._app.agent.save()
            case key.SPACE:
                if self._step_by_step:
                    self._update_state(self._app.board.state)
                    self._app.update()

    def _init_board_display(self: Self) -> list[list[Sprite]]:
        """Initialize the board tiles.

        Returns:
            list[list[Sprite]]: A matrix of tiles.
        """
        offset = self._height - 1
        return [
            [
                Sprite(
                    self._atlas[0],
                    self._tile_size * j,
                    self._tile_size * (offset - i),
                    batch=self._batch,
                )
                for j in range(self._width)
            ]
            for i in range(self._height)
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

    def _update_state(self: Self, board_state: ndarray) -> None:
        """Update the tile matrix to correspond to the board state.

        Args:
            board_state (ndarray): current state of the board.
        """
        self._app.interpreter.terminal_display()
        for i in range(board_state.shape[0]):
            for j in range(board_state.shape[1]):
                match board_state[i, j]:
                    case Board.W:
                        self._tiles[i][j].image = self._atlas[3]
                    case Board.H:
                        self._tiles[i][j].image = self._atlas[5]
                    case Board.S:
                        self._tiles[i][j].image = self._atlas[4]
                    case Board.G:
                        self._tiles[i][j].image = self._atlas[2]
                    case Board.R:
                        self._tiles[i][j].image = self._atlas[1]
                    case _:
                        self._tiles[i][j].image = self._atlas[0]

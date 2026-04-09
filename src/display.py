"""Display module manages the graphic interface."""

import sys
from typing import Self, Any

import numpy as np
import matplotlib.pyplot as plt
import pyglet as pyg
import time
from numpy import ndarray
from pyglet.graphics import Batch
from pyglet.image import SolidColorImagePattern, Texture
from pyglet.sprite import Sprite
from pyglet.window import key

from board import Board
from trainer import Trainer


class Display:
    """Manage the graphic interface."""

    def __init__(
        self: Self,
        app: Trainer,
        sleep: float = 0,
        savepath: str = None,
        i: int = None
    ) -> None:
        """Display instanciation

        Args:
            app (Trainer): The app to display.
            sleep (float): Initial sleep time between iterations.
            savepath (str): Savepath of the agent.
            i (int): Index of the display
        """
        self._app = app
        self._sleep = sleep
        self._last_time = time.time()
        self._step_by_step = False
        self._index = i
        self._savepath = savepath
        self._closed = False
        self._done = False
        self._tile_size = 32
        width, height = app.interpreter.board.shape
        self._width, self._height = width + 2, height + 2
        width = self._tile_size * self._width
        height = self._tile_size * self._height
        if sys.platform == "darwin":
            width /= 2
            height /= 2
        self._window = pyg.window.Window(width=width, height=height)
        self._window.set_caption(f"{savepath or "agent"}({i})")
        self._atlas = self._init_atlas()
        self._batch = Batch()
        self._tiles = self._init_board_display()
        self._window.push_handlers(on_draw=self.on_draw)
        self._window.push_handlers(on_key_press=self.on_key_press)
        self._window.push_handlers(on_close=self.on_close)
        self._init_graph()

    @property
    def closed(self: Self) -> bool:
        """State of the window.

        Returns:
            bool: True if close, False otherwise.
        """
        return self._closed

    @property
    def index(self: Self) -> int:
        """Index of the display session.

        Returns:
            int: The display session's index.
        """
        return self._index

    def run(self: Self) -> None:
        """Run the event loop."""
        pyg.app.run()

    def close(self: Self) -> None:
        """Close the display loop."""
        pyg.clock.schedule_once(self._close, 0)

    def on_close(self: Self, _: Any = None) -> None:
        """Close the app.

        _ (Any): Unused parameter.
        """
        self._app.agent.save(self._savepath, self._index)
        self._app.interpreter.clear_terminal_display()
        self._closed = True

    def on_draw(self: Self) -> None:
        """Display event function."""
        self._window.clear()
        now = time.time()
        if not self._step_by_step and now - self._last_time > self._sleep:
            self._update_state(self._app.board.state)
            if self._done or self._app.update():
                self._done = True
            self._last_time = now
        self._batch.draw()
        self._update_graph()

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
                self._app.agent.save(self._savepath, self._index)
            case key.SPACE:
                if self._step_by_step:
                    self._update_state(self._app.board.state)
                    if not self._done:
                        self._app.update()

    def save(self: Self, savepath: str = None, index: int = None) -> None:
        """Save the current step of the app.

        Args:
            savepath (str): path of the file.
            index (int): index for multiple file save with the same name
        """
        self._app.agent.save(savepath, index)

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

    def _init_graph(self: Self) -> None:
        """Initialize stat graph."""
        plt.ion()
        plt.show(block=False)
        self._fig = plt.figure()
        self._ax = self._fig.add_axes((0.1, 0.1, 0.8, 0.8))
        self._time_line, = self._ax.plot(self._app.iterations, self._app.times)
        self._len_line, = self._ax.plot(
            self._app.iterations, self._app.lengths
        )

    def _update_graph(self: Self) -> None:
        """Update the stat graph."""
        self._time_line.set_data(self._app.iterations, self._app.times)
        self._len_line.set_data(self._app.iterations, self._app.lengths)
        self._ax.relim()
        self._ax.autoscale_view()
        plt.pause(0.001)
        print(self._app.iterations)

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

    def _close(self: Self, *_: list) -> None:
        """Close the display loop.

        Args:
            _ (list): Parameters for the schedule call (unused).
        """
        self._window.close()
        self.on_close()

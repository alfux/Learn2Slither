"""Display module manages the graphic interface."""

import time
from typing import Self

import pyglet
from pyglet.graphics import Batch
from pyglet.image import SolidColorImagePattern, Texture
from pyglet.sprite import Sprite
from pyglet.window import key

from agent import Agent
from board import Board


class Display:
    """Manage the graphic interface."""

    def __init__(self: Self, agent: Agent) -> None:
        """Display instanciation"""
        self._window = pyglet.window.Window()
        self._agent = agent
        self._tile_size = 32
        self._atlas = self._init_atlas()
        self._floor = self._atlas[0]
        self._wall = self._atlas[3]
        self._green_apple = self._atlas[2]
        self._red_apple = self._atlas[1]
        self._snake = self._atlas[4]
        self._head = self._atlas[5]
        self._height, self._width = self._agent.board.state.shape
        self._batch = Batch()
        self._tiles = self._init_board_display()
        self._window.push_handlers(on_draw=self.on_draw)
        self._window.set_size(
            width=(self._tile_size * self._width),
            height=(self._tile_size * self._height),
        )

    def run(self: Self) -> None:
        """Run the event loop."""
        pyglet.app.run()

    def close(self: Self) -> None:
        """Close the event loop."""
        self._window.close()

    def on_draw(self: Self) -> None:
        """Display event function."""
        self._window.clear()
        self._update_state()
        self._batch.draw()
        item = self._agent.play(0.4)
        match item:
            case Board.W:
                self._agent.learn(0)
                self._agent.board.reset()
                print("Dead by wall")
            case Board.H:
                self._agent.learn(0)
                self._agent.board.reset()
                print("Dead by head")
            case Board.S:
                self._agent.learn(0)
                self._agent.board.reset()
                print("Dead by body")
            case -1:
                self._agent.learn(0)
                self._agent.board.reset()
                print("Dead by size")
            case Board.G:
                self._agent.learn(1)
                print("Miam")
            case Board.R:
                self._agent.learn(0.2)
                print("Eww")
            case _:
                self._agent.learn(0.3)

    def _init_board_display(self: Self) -> list[list[Sprite]]:
        """Initialize the board tiles.

        Returns:
            list[list[Sprite]]: A matrix of tiles.
        """
        n, m = self._agent.board.state.shape
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
        for i in range(self._agent.board.state.shape[0]):
            for j in range(self._agent.board.state.shape[1]):
                match self._agent.board.state[i, j]:
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

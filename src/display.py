"""Display module manages the graphic interface."""

from typing import Self
import time

import pyglet


class Display:
    """Display creating and managing the graphic interface."""

    def __init__(self: Self) -> None:
        """Display instanciation"""
        self._window = pyglet.window.Window(width=800, height=450)
        self._window.push_handlers(on_draw=self.on_draw)
        color = pyglet.image.SolidColorImagePattern((34, 139, 34, 255))
        image = color.create_image(32, 32)
        self._tile = pyglet.sprite.Sprite(image, x=0, y=0)

    def run(self: Self) -> None:
        """Run the event loop."""
        pyglet.app.run()

    def close(self: Self) -> None:
        """Close the event loop."""
        self._window.close()

    def on_draw(self: Self) -> None:
        """Dispplay event function."""
        self._window.clear()
        self._tile.draw()

"""Menu manager module."""

from typing import Self, Any

import pyglet as pyg

from button import Button
from display import Display


class Menu:
    """Manage menu, buttons, statistics."""

    def __init__(self: Self) -> None:
        """Initialize the game."""
        self._window = pyg.window.Window(caption="Menu")
        self._batch = pyg.graphics.Batch()
        self._buttons = [
            Button(0, 100, 100, 50, "Lolo", (100, 0, 0),
                   (200, 0, 0), (255, 0, 0), (255, 0, 0), batch=self._batch),
            Button(0, 200, 100, 50, "Haha", (0, 100, 0),
                   (0, 200, 0), (0, 255, 0), (0, 255, 0), batch=self._batch),
            Button(0, 300, 100, 50, "Ouch", (0, 0, 100),
                   (0, 0, 200), (0, 0, 255), (0, 0, 255), batch=self._batch)
        ]
        self._game: Display = None
        self._window.on_draw = self.on_draw
        self._window.on_mouse_motion = self.on_mouse_motion
        self._window.on_mouse_press = self.on_mouse_press
        self._window.on_mouse_release = self.on_mouse_release

    def run(self: Self) -> None:
        """Run the app."""
        pyg.app.run()

    def on_draw(self: Self) -> None:
        """Main draw routine."""
        self._window.clear()
        if self._game is not None:
            self._game.on_draw()
        self._batch.draw()

    def on_mouse_motion(self: Self, x: int, y: int, dx: int, dy: int) -> None:
        """Handle mouse motions.

        Args:
            x (int): x component of the position of the mouse.
            y (int): y component of the position of the mouse.
            dx (int): dx component of the speed of the mouse.
            dy (int): dy component of the speed of the mouse.
        """
        for button in self._buttons:
            if button.is_hovered(x, y, False):
                print(x, y, dx, dy)

    def on_mouse_press(self: Self, x: int, y: int, btn: int, mod: int) -> None:
        """Handle mouse press.

        Args:
            x (int): x component of the position of the click.
            y (int): y component of the position of the click.
            btn (int): button presed.
            mod (int): modifier.
        """
        for button in self._buttons:
            if button.is_hovered(x, y, True):
                print(x, y, btn, mod)

    def on_mouse_release(self: Self, x: int, y: int, btn: int, mod: int) -> None:
        """Handle mouse press.

        Args:
            x (int): x component of the position of the click.
            y (int): y component of the position of the click.
            btn (int): button presed.
            mod (int): modifier.
        """
        for button in self._buttons:
            if button.is_hovered(x, y, False):
                print(x, y, btn, mod)

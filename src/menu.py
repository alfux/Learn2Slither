"""Menu manager module."""

from pathlib import Path
import sys
from typing import Self

import pyglet as pyg

from button import Button
from display import Display
from learn2slither import Learn2Slither


class Menu:
    """Manage menu, buttons, statistics."""

    def __init__(self: Self, w: int = 900, h: int = 600) -> None:
        """Initialize the game."""
        self._window = pyg.window.Window(caption="Menu", width=w, height=h)
        if sys.platform == "darwin":
            self._window.set_size(w / 2, h / 2)
        self._batch = pyg.graphics.Batch()
        self._game: Display = None
        self._window.on_draw = self.on_draw
        self._window.on_mouse_motion = self.on_mouse_motion
        self._window.on_mouse_press = self.on_mouse_press
        self._window.on_mouse_release = self.on_mouse_release
        self._parameters = self._default_parameters()
        self._init_menu()

    def _init_menu(self: Self) -> None:
        """Initialize the menu."""
        self._menu_title = pyg.text.Label(
            "Menu",
            0.5 * self._window.width,
            0.9 * self._window.height,
            font_size=64,
            anchor_x="center",
            anchor_y="center",
            batch=self._batch
        )
        self._option_title = pyg.text.Label(
            "Options",
            0.7 * self._window.width,
            0.7 * self._window.height,
            font_size=32,
            anchor_x="center",
            anchor_y="center",
            batch=self._batch
        )
        self._buttons = [
            Button(
                0.1 * self._window.width,
                0.4 * self._window.height,
                0.3 * self._window.width,
                0.2 * self._window.height,
                label="Start",
                font_size=22,
                color=(0, 100, 0),
                hover=(0, 150, 0),
                batch=self._batch,
                callback=self._start_button_callback
            ),
            Button(
                0.6 * self._window.width,
                0.5 * self._window.height,
                0.1 * self._window.width,
                0.1 * self._window.height,
                label="Learn",
                font_size=22,
                color=(100, 0, 0),
                batch=self._batch,
                toggle=(0, 200, 0),
                toggled=True,
                callback=self._learn_button_callback
            )
        ]

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
            button.is_hovered(x, y)

    def on_mouse_press(self: Self, x: int, y: int, btn: int, _: int) -> None:
        """Handle mouse press.

        Args:
            x (int): x component of the position of the click.
            y (int): y component of the position of the click.
            btn (int): button presed.
            _ (int): modifier (unused).
        """
        if btn == 1:
            for button in self._buttons:
                if button.is_clicked(x, y):
                    button()

    def on_mouse_release(self: Self, x: int, y: int, btn: int, _: int) -> None:
        """Handle mouse press.

        Args:
            x (int): x component of the position of the click.
            y (int): y component of the position of the click.
            btn (int): button presed.
            _ (int): modifier (unused).
        """
        if btn == 1:
            for button in self._buttons:
                button.is_hovered(x, y)

    def _start_button_callback(self: Self) -> None:
        """Start a training / game session with current parameters."""
        l2s = Learn2Slither(**self._parameters)
        if self._parameters["no_display"]:
            l2s.train()
            l2s.agent.save()
        else:
            Display(l2s)

    def _learn_button_callback(self: Self) -> None:
        """Learn button callback."""
        self._parameters["no_learn"] = not self._parameters["no_learn"]

    def _default_parameters(self: Self) -> dict:
        """Generate default parameters.

        Returns:
            dict: Default parameters.
        """
        return {
            "agent": Path(__file__).resolve().parent / "default.json",
            "no_learn": False,
            "no_display": False,
            "sessions": 1000,
            "board_size": 10
        }

"""Menu manager module."""

from pathlib import Path
import sys
from typing import Self, Callable
from tkinter import filedialog

import pyglet as pyg

from button import Button
from display import Display
from trainer import Trainer


class Menu:
    """Manage menu, buttons, statistics."""

    def __init__(self: Self, w: int = 900, h: int = 600, **kw: dict) -> None:
        """Initialize the game.

        Args:
            w (int): Width of the menu.
            h (int): Height of the menu.
        KWArgs:
            **kw (dict): Default parameters.
        """
        self._window = pyg.window.Window(caption="Menu", width=w, height=h)
        pyg.gl.glClearColor(100 / 255, 100 / 255, 100 / 255, 1)
        if sys.platform == "darwin":
            self._window.set_size(w / 2, h / 2)
        self._batch = pyg.graphics.Batch()
        self._game: Display = None
        self._window.on_draw = self.on_draw
        self._window.on_mouse_motion = self.on_mouse_motion
        self._window.on_mouse_press = self.on_mouse_press
        self._window.on_mouse_release = self.on_mouse_release
        self._parameters = self._default_parameters(kw)
        self._background_trainer: list[Trainer] = []
        self._stop_background_trainer: list[Callable] = []
        self._display_trainer: list[Display] = []
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
            0.775 * self._window.width,
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
                color=(0, 200, 0),
                hover=(0, 150, 0),
                batch=self._batch,
                callback=self._start_button_callback
            ),
            Button(
                0.1 * self._window.width,
                0.15 * self._window.height,
                0.3 * self._window.width,
                0.2 * self._window.height,
                label="Stop",
                font_size=22,
                color=(200, 0, 0),
                hover=(150, 0, 0),
                batch=self._batch,
                callback=self._stop_button_callback
            ),
            Button(
                0.6 * self._window.width,
                0.5 * self._window.height,
                0.15 * self._window.width,
                0.12 * self._window.height,
                label="Learn",
                font_size=22,
                color=(200, 0, 0),
                batch=self._batch,
                toggle=(0, 200, 0),
                toggled=True,
                callback=self._learn_button_callback
            ),
            Button(
                0.8 * self._window.width,
                0.5 * self._window.height,
                0.15 * self._window.width,
                0.12 * self._window.height,
                label="Display",
                font_size=22,
                color=(200, 0, 0),
                batch=self._batch,
                toggle=(0, 200, 0),
                toggled=True,
                callback=self._display_button_callback
            ),
            Button(
                0.6 * self._window.width,
                0.3 * self._window.height,
                0.15 * self._window.width,
                0.12 * self._window.height,
                label="Save",
                font_size=22,
                color=(0, 200, 0),
                hover=(0, 150, 0),
                batch=self._batch,
                callback=self._save_button_callback
            ),
            Button(
                0.8 * self._window.width,
                0.3 * self._window.height,
                0.15 * self._window.width,
                0.12 * self._window.height,
                label="SaveAs",
                font_size=22,
                color=(0, 200, 0),
                hover=(0, 150, 0),
                batch=self._batch,
                callback=self._save_as_button_callback
            ),
            Button(
                0.6 * self._window.width,
                0.1 * self._window.height,
                0.15 * self._window.width,
                0.12 * self._window.height,
                label="Load",
                font_size=22,
                color=(0, 200, 0),
                hover=(0, 150, 0),
                batch=self._batch,
                callback=self._load_button_callback
            ),
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
        self._background_trainer = [
            trainer for trainer in self._background_trainer if trainer.running
        ]
        self._stop_background_trainer = [
            trainer.stop for trainer in self._background_trainer
        ]
        self._display_trainer = [
            display for display in self._display_trainer if not display.closed
        ]

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
        index = len(self._background_trainer) + len(self._display_trainer)
        if self._parameters["no_display"]:
            trainer = Trainer(**self._parameters)
            self._background_trainer.append(trainer)
            self._stop_background_trainer.append(trainer.stop)
            trainer.train(self._parameters["savepath"], index)
        else:
            self._display_trainer.append(Display(
                Trainer(**self._parameters),
                sleep=0,
                savepath=self._parameters["savepath"],
                i=index
            ))

    def _stop_button_callback(self: Self) -> None:
        """Stop all running sessions."""
        for stop in self._stop_background_trainer:
            stop()
        for display in self._display_trainer:
            pyg.clock.schedule_once(display.on_close, 0)

    def _learn_button_callback(self: Self) -> None:
        """Toggle no_learn parameter."""
        self._parameters["no_learn"] = not self._parameters["no_learn"]

    def _display_button_callback(self: Self) -> None:
        """Toggle no_display parameter."""
        self._parameters["no_display"] = not self._parameters["no_display"]

    def _load_button_callback(self: Self) -> None:
        """Browse for an agent file."""
        self._parameters["agent"] = filedialog.askopenfilename(
            defaultextension=".json"
        )

    def _save_as_button_callback(self: Self) -> None:
        """Choose a filename for saves."""
        savepath = filedialog.asksaveasfilename(defaultextension=".json")
        for display in self._display_trainer:
            display.save(savepath, display.index)
        i = len(self._display_trainer)
        for trainer in self._background_trainer:
            trainer.save(savepath, i)
            i += 1

    def _save_button_callback(self: Self) -> None:
        """Save all instances."""
        for display in self._display_trainer:
            display.save(self._parameters["savepath"], display.index)
        i = len(self._display_trainer)
        for trainer in self._background_trainer:
            trainer.save(self._parameters["savepath"], i)
            i += 1

    def _default_parameters(self: Self, kw: dict) -> dict:
        """Generate default parameters.

        Returns:
            dict: Default parameters.
        """
        if kw["agent"] is None:
            kw["agent"] = Path(__file__).resolve().parent / "default.json"
        return kw

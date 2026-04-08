"""Menu manager module."""

from pathlib import Path
import sys
from typing import Self, Callable

import crossfiledialog as cfd
import numpy as np
import pyglet as pyg
from pyglet.window import key

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
        self._batch = pyg.graphics.Batch()
        self._game: Display = None
        self._window.push_handlers(on_draw=self.on_draw)
        self._window.push_handlers(on_mouse_motion=self.on_mouse_motion)
        self._window.push_handlers(on_mouse_press=self.on_mouse_press)
        self._window.push_handlers(on_mouse_release=self.on_mouse_release)
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
            0.75 * self._window.height,
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
                0.55 * self._window.height,
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
                0.55 * self._window.height,
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
                0.35 * self._window.height,
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
                0.35 * self._window.height,
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
                0.15 * self._window.height,
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
        self._session_title = pyg.text.Label(
            "Sessions",
            0.8 * self._window.width,
            0.25 * self._window.height,
            font_size=22,
            anchor_x="left",
            anchor_y="center",
            batch=self._batch
        )
        self._blank_text_field = pyg.shapes.Rectangle(
            0.8 * self._window.width,
            0.19 * self._window.height,
            0.15 * self._window.width,
            0.04 * self._window.height,
            (255, 255, 255),
            batch=self._batch
        )
        self._document = pyg.text.document.UnformattedDocument(
            str(self._parameters["sessions"])
        )
        self._document.set_style(0, 0, {"font_size": 22})
        layout = pyg.text.layout.IncrementalTextLayout(
            self._document,
            0.93 * self._window.width,
            0.19 * self._window.height,
            width=0.15 * self._window.width,
            height=0.06 * self._window.height,
            anchor_x="center",
            anchor_y="center",
            multiline=False,
            batch=self._batch
        )
        self._caret = pyg.text.caret.Caret(layout)
        self._window.push_handlers(
            on_text=self._no_return(self._caret.on_text)
        )
        self._window.push_handlers(
            on_text_motion=self._no_return(self._caret.on_text_motion)
        )
        self._window.push_handlers(
            on_text_motion_select=self._no_return(
                self._caret.on_text_motion_select
            )
        )
        self._window.push_handlers(
            on_mouse_press=self._no_return(self._caret.on_mouse_press)
        )
        self._gauge_x_min = 0.6 * self._window.width
        self._gauge_y_min = 0.04 * self._window.height
        self._gauge_width = 0.35 * self._window.width
        self._gauge_height = 0.04 * self._window.height
        self._gauge_x_max = self._gauge_x_min + self._gauge_width
        self._gauge_y_max = self._gauge_y_min + self._gauge_height
        self._blank_gauge = pyg.shapes.Rectangle(
            self._gauge_x_min,
            self._gauge_y_min,
            self._gauge_width,
            self._gauge_height,
            (255, 255, 255),
            batch=self._batch
        )
        self._green__gauge = pyg.shapes.Rectangle(
            self._gauge_x_min,
            self._gauge_y_min,
            0,
            self._gauge_height,
            (0, 255, 0),
            batch=self._batch
        )
        self._gauge_clicked = False
        self._window.push_handlers(on_mouse_drag=self.on_mouse_drag)

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

    def on_key_press(self: Self, symbol: int, _: int) -> None:
        """Keyboard event function.

        Args:
            symbol (int): The key symbol.
            _ (int): The modifier (unused).
        """
        if symbol == key.ENTER:
            try:
                sessions = int("".join(self._document.text.split()))
                self._parameters["sessions"] = sessions
            except Exception:
                pass
            finally:
                self._document.delete_text(0, len(self._document.text))
                self._document.insert_text(
                    0, str(self._parameters["sessions"])
                )

    def on_mouse_drag(
        self: Self, x: int, y: int, dx: int, dy: int, btn: int, mod: int
    ) -> None:
        """Handle drag motions.

        Args:
            x (int): x component of the position of the mouse.
            y (int): y component of the position of the mouse.
            dx (int): dx component of the speed of the mouse.
            dy (int): dy component of the speed of the mouse.
            btn (int): button presed.
            mod (int): button modifier.
        """
        if self._gauge_clicked:
            self._speed_gauge_callback(x)

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
            if self._gauge_x_min <= x <= self._gauge_x_max:
                if self._gauge_y_min <= y <= self._gauge_y_max:
                    self._gauge_clicked = True
                    self._speed_gauge_callback(x)

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
        self._gauge_clicked = False

    def _speed_gauge_callback(self: Self, x: float) -> None:
        """Update the speed gauge.

        Args:
            x (float): X position of the mouse.
        """
        self._green__gauge.width = x - self._gauge_x_min

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
                sleep=self._parameters["sleep"],
                savepath=self._parameters["savepath"],
                i=index
            ))

    def _stop_button_callback(self: Self) -> None:
        """Stop all running sessions."""
        for stop in self._stop_background_trainer:
            stop()
        for display in self._display_trainer:
            pyg.clock.schedule_once(display.window.close, 0)

    def _learn_button_callback(self: Self) -> None:
        """Toggle no_learn parameter."""
        self._parameters["no_learn"] = not self._parameters["no_learn"]

    def _display_button_callback(self: Self) -> None:
        """Toggle no_display parameter."""
        self._parameters["no_display"] = not self._parameters["no_display"]

    def _load_button_callback(self: Self) -> None:
        """Browse for an agent file."""
        self._parameters["agent"] = cfd.open_file(
            "Load an agent", filter=".json"
        )

    def _save_as_button_callback(self: Self) -> None:
        """Choose a filename for saves."""
        savepath = cfd.save_file("Save agent")
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

    def _no_return(self: Self, func: Callable) -> Callable:
        """Prevent any return from the function.

        Args:
            func (Callable): function intercepting return.
        Returns:
            Callable: new function without return.
        """

        def callback(*av: list, **kw: dict) -> None:
            """Function without return.

            Args:
                *av (list): any positional arguments.
            KWArgs:
                **kw (dict): any keyword arguments.
            """
            func(*av, *kw)

        return callback

    def _default_parameters(self: Self, kw: dict) -> dict:
        """Generate default parameters.

        Returns:
            dict: Default parameters.
        """
        if kw["agent"] is None:
            kw["agent"] = Path(__file__).resolve().parent / "default.json"
        if "sleep" not in kw.keys():
            kw["sleep"] = 0
        else:
            self._parameters["sleep"] = np.clip(
                self._parameters["sleep"], 0, 1
            )
        return kw

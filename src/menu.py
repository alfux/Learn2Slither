"""Menu manager module."""

from pathlib import Path
from typing import Self, Callable

import crossfiledialog as cfd
import numpy as np
import pyglet as pyg
from pyglet.graphics import Batch
from pyglet.window import key, Window

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
        self._window = Window(caption="Menu", width=w, height=h)
        self._field_window = None
        self._field_batch = None
        pyg.gl.glClearColor(100 / 255, 100 / 255, 100 / 255, 1)
        self._batch = Batch()
        self._window.push_handlers(on_draw=self.on_draw)
        self._window.push_handlers(on_mouse_motion=self.on_mouse_motion)
        self._window.push_handlers(on_mouse_press=self.on_mouse_press)
        self._window.push_handlers(on_mouse_release=self.on_mouse_release)
        self._parameters = self._default_parameters(kw)
        self._background_trainer: list[Trainer] = []
        self._stop_background_trainer: list[Callable] = []
        self._display_trainer: list[Display] = []
        self._init_menu()

    def run(self: Self) -> None:
        """Run the app."""
        pyg.app.run()

    def on_draw(self: Self) -> None:
        """Main draw routine."""
        self._window.clear()
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
                self._parameters[self._current_field] = sessions
                pyg.clock.schedule_once(self._close_field_window, 0)
            except Exception:
                pass
            finally:
                self._document.delete_text(0, len(self._document.text))
                self._document.insert_text(
                    0, str(self._parameters[self._current_field])
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

    def _init_menu(self: Self) -> None:
        """Initialize the menu."""
        self._init_menu_title()
        self._init_option_title()
        self._init_buttons()
        self._init_speed_title()
        self._init_speed_gauge()

    def _init_menu_title(self: Self) -> None:
        """Initialize Menu title."""
        self._menu_title = pyg.text.Label(
            "Menu",
            0.5 * self._window.width,
            0.9 * self._window.height,
            font_size=64,
            anchor_x="center",
            anchor_y="center",
            batch=self._batch
        )

    def _init_option_title(self: Self) -> None:
        """Initialize Option title."""
        self._option_title = pyg.text.Label(
            "Options",
            0.775 * self._window.width,
            0.75 * self._window.height,
            font_size=32,
            anchor_x="center",
            anchor_y="center",
            batch=self._batch
        )

    def _init_buttons(self: Self) -> None:
        """Initialize buttons."""
        self._buttons = [
            self._init_start_button(),
            self._init_stop_button(),
            self._init_learn_button(),
            self._init_display_button(),
            self._init_save_button(),
            self._init_save_as_button(),
            self._init_load_button(),
            self._init_session_button(),
            self._init_size_button()
        ]

    def _init_start_button(self: Self) -> Button:
        """Create Start button.

        Returns:
            Button: Start button.
        """
        return Button(
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
        )

    def _init_stop_button(self: Self) -> Button:
        """Create Stop button.

        Returns:
            Button: Stop button.
        """
        return Button(
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
        )

    def _init_learn_button(self: Self) -> Button:
        """Create Learn button.

        Returns:
            Button: Learn button.
        """
        return Button(
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
        )

    def _init_display_button(self: Self) -> Button:
        """Create Display button.

        Returns:
            Button: Display button.
        """
        return Button(
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
        )

    def _init_save_button(self: Self) -> Button:
        """Create Save button.

        Returns:
            Button: Save button.
        """
        return Button(
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
        )

    def _init_save_as_button(self: Self) -> Button:
        """Create SaveAs button.

        Returns:
            Button: SaveAs button.
        """
        return Button(
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
        )

    def _init_load_button(self: Self) -> Button:
        """Create Load button.

        Returns:
            Button: Load button.
        """
        return Button(
            0.6 * self._window.width,
            0.2 * self._window.height,
            0.15 * self._window.width,
            0.12 * self._window.height,
            label="Load",
            font_size=22,
            color=(0, 200, 0),
            hover=(0, 150, 0),
            batch=self._batch,
            callback=self._load_button_callback
        )

    def _init_session_button(self: Self) -> Button:
        """Init session button."""
        return Button(
            0.8 * self._window.width,
            0.2 * self._window.height,
            0.15 * self._window.width,
            0.12 * self._window.height,
            label="Sessions",
            font_size=22,
            color=(0, 200, 0),
            hover=(0, 150, 0),
            batch=self._batch,
            callback=self._session_button_callback
        )

    def _init_size_button(self: Self) -> Button:
        """Init session button."""
        return Button(
            0.8 * self._window.width,
            0.05 * self._window.height,
            0.15 * self._window.width,
            0.12 * self._window.height,
            label="Size",
            font_size=22,
            color=(0, 200, 0),
            hover=(0, 150, 0),
            batch=self._batch,
            callback=self._size_button_callback
        )

    def _init_speed_title(self: Self) -> None:
        """Init speed title."""
        self._speed_title = pyg.text.Label(
            "Speed",
            0.6 * self._window.width,
            0.15 * self._window.height,
            font_size=22,
            anchor_x="left",
            anchor_y="center",
            batch=self._batch
        )

    def _init_speed_gauge(self: Self) -> None:
        """Init speed gauge."""
        self._gauge_x_min = 0.6 * self._window.width
        self._gauge_y_min = 0.07 * self._window.height
        self._gauge_width = 0.15 * self._window.width
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
        self._green_gauge = pyg.shapes.Rectangle(
            self._gauge_x_min,
            self._gauge_y_min,
            (1 - self._parameters["sleep"]) * self._gauge_width,
            self._gauge_height,
            (0, 255, 0),
            batch=self._batch
        )
        self._gauge_clicked = False
        self._window.push_handlers(on_mouse_drag=self.on_mouse_drag)

    def _speed_gauge_callback(self: Self, x: float) -> None:
        """Update the speed gauge.

        Args:
            x (float): X position of the mouse.
        """
        self._green_gauge.width = np.clip(
            x - self._gauge_x_min, 0, self._gauge_width
        )
        self._parameters["sleep"] = (
            1 - self._green_gauge.width / self._gauge_width
        )

    def _start_button_callback(self: Self) -> None:
        """Start a training / game session with current parameters."""
        index = len(self._background_trainer) + len(self._display_trainer)
        max_thread = len(self._background_trainer) + len(self._display_trainer)
        if max_thread < self._parameters["max_thread"]:
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
        else:
            print("Max thread reached !")

    def _stop_button_callback(self: Self) -> None:
        """Stop all running sessions."""
        for stop in self._stop_background_trainer:
            stop()
        for display in self._display_trainer:
            display.close()

    def _learn_button_callback(self: Self) -> None:
        """Toggle no_learn parameter."""
        self._parameters["no_learn"] = not self._parameters["no_learn"]

    def _display_button_callback(self: Self) -> None:
        """Toggle no_display parameter."""
        self._parameters["no_display"] = not self._parameters["no_display"]

    def _load_button_callback(self: Self) -> None:
        """Browse for an agent file."""
        self._parameters["agent"] = cfd.open_file(
            "Load an agent", filter="*.json"
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

    def _session_button_callback(self: Self) -> None:
        """Open a window to enter session number."""
        if self._field_window is None:
            self._current_field = "sessions"
            self._open_field_window("Session")

    def _size_button_callback(self: Self) -> None:
        """Open a window to enter size of the board."""
        if self._field_window is None:
            self._current_field = "board_size"
            self._open_field_window("Board size")

    def _open_field_window(self: Self, title: str) -> None:
        """Open a field window with a title."""
        self._field_window = Window(width=500, height=100)
        pyg.gl.glClearColor(100 / 255, 100 / 255, 100 / 255, 1)
        self._field_window.set_caption(title)
        self._field_batch = Batch()
        self._init_session_field()
        self._push_session_field_handlers()

    def _init_session_field(self: Self) -> None:
        """Init session field."""
        self._blank_text_field = pyg.shapes.Rectangle(
            0.25 * self._field_window.width,
            0.25 * self._field_window.height,
            0.5 * self._field_window.width,
            0.5 * self._field_window.height,
            (255, 255, 255),
            batch=self._field_batch
        )
        self._document = pyg.text.document.UnformattedDocument(
            str(self._parameters[self._current_field])
        )
        self._document.set_style(0, 0, {"font_size": 18})
        layout = pyg.text.layout.IncrementalTextLayout(
            self._document,
            0.25 * self._field_window.width,
            0.6 * self._field_window.height,
            width=0.5 * self._field_window.width,
            height=self._field_window.height,
            anchor_x="left",
            anchor_y="top",
            multiline=False,
            batch=self._field_batch
        )
        self._caret = pyg.text.caret.Caret(layout)

    def _push_session_field_handlers(self: Self) -> None:
        """Register session field handlers."""
        self._field_window.push_handlers(
            on_text=self._no_return(self._caret.on_text)
        )
        self._field_window.push_handlers(
            on_text_motion=self._no_return(self._caret.on_text_motion)
        )
        self._field_window.push_handlers(
            on_text_motion_select=self._no_return(
                self._caret.on_text_motion_select
            )
        )
        self._field_window.push_handlers(
            on_mouse_press=self._no_return(self._caret.on_mouse_press)
        )
        self._field_window.push_handlers(on_key_press=self.on_key_press)
        self._field_window.push_handlers(on_draw=self._field_on_draw)
        self._field_window.push_handlers(on_close=self._field_on_close)

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

    def _field_on_draw(self: Self) -> None:
        """Draw the field window's content."""
        self._field_window.clear()
        self._field_batch.draw()

    def _close_field_window(self: Self, *_: list) -> None:
        """Close a field window.

        Args:
            *_ (list): Any args, unused."""
        self._field_window.close()
        self._field_on_close()

    def _field_on_close(self: Self) -> None:
        """Field window close handler."""
        self._field_window = None
        self._field_batch = None

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
        if "max_thread" not in kw.keys():
            self._parameters["max_thread"] = 1
        return kw

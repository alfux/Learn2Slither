"""Button module defines button class."""

from typing import Any, Callable, Self

import pyglet as pyg


class Button:
    """Define a diplayable button for pyglet."""

    def __init__(
        self: Self,
        x: int,
        y: int,
        w: int,
        h: int,
        *,
        label: str = "",
        font_size: int = 12,
        color: tuple = (255, 255, 255),
        hover: tuple = None,
        click: tuple = None,
        toggle: tuple = None,
        toggled: bool = False,
        batch: pyg.graphics.Batch = None,
        callback: Callable = None
    ) -> None:
        """Define the button object.s

        Args:
            x (int): x component of position.
            y (int): y component of position.
            w (int): Width of the button.
            h (int): Height of the button.
            label (str): Label of the button.
            color (tuple): Color of the button.
            hover (tuple): Color of the button when hovering.
            click (tuple): Color of the button when clicking.
            toggle (tuple): (Optional) Set a color for a toggle button.
            toggled (bool) (Optional) Set True to initialize as toggled.
            batch (Batch): (Optional) Drawing batch
        """
        self._x_min = x
        self._x_max = x + w
        self._y_min = y
        self._y_max = y + h
        self._color = color
        self._hover = hover
        self._click = click
        self._toggle = toggle
        self._toggled = toggled
        self._callback: Callable = callback
        self._button = pyg.shapes.Rectangle(
            x, y, w, h, toggle if toggled else color, batch=batch
        )
        self._label = pyg.text.Label(
            label,
            x + w // 2,
            y + h // 2,
            font_size=font_size,
            anchor_x="center",
            anchor_y="center",
            batch=batch
        )

    def __call__(self: Self, *av: list, **kw: dict) -> Any:
        """Call the assigned callback function.

        Args:
            *av (list): list of positional arguments.
        KWArgs:
            **kw (dict): list of keyword arguments.
        Returns:
            Any: The callback retrun or None.
        """
        if self._callback is not None:
            return self._callback(*av, **kw)

    def is_hovered(self: Self, x: int, y: int) -> bool:
        """Detect hovering of the button.

        Args:
            x (int): x component of the mouse position.
            y (int): y component of the mouse position.
            click (bool): Set True if a click happened.
        Returns:
            bool: True if hovered, False otherwise.
        """
        if self._x_min <= x <= self._x_max and self._y_min <= y <= self._y_max:
            if self._hover is not None:
                self._button.color = self._hover
            elif self._toggled:
                self._button.color = self._toggle
            else:
                self._button.color = self._color
            return True
        self._button.color = self._toggle if self._toggled else self._color
        return False

    def is_clicked(self: Self, x: int, y: int) -> bool:
        """Detect click of the button.

        Args:
            x (int): x component of the mouse position.
            y (int): y component of the mouse position.
        Returns:
            bool: True if clicked, False otherwise.
        """
        if self._x_min <= x <= self._x_max and self._y_min <= y <= self._y_max:
            if self._toggle is not None:
                self._toggled = not self._toggled
            if self._click is not None:
                self._button.color = self._click
            elif self._toggled:
                self._button.color = self._toggle
            else:
                self._button.color = self._color
            return True
        else:
            self._button.color = self._toggle if self._toggled else self._color
            return False

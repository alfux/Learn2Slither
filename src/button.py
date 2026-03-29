"""Button module defines button class."""

from typing import Self

import pyglet as pyg


class Button:
    """Define a diplayable button for pyglet."""

    def __init__(
        self: Self,
        x: int,
        y: int,
        w: int,
        h: int,
        label: str,
        color: tuple,
        hover: tuple,
        click: tuple,
        toggle: tuple = None,
        toggled: bool = False,
        batch: pyg.graphics.Batch = None
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
        self._button = pyg.shapes.Rectangle(x, y, w, h, color, batch=batch)
        self._label = pyg.text.Label(
            label,
            x + w // 2,
            y + h // 2,
            font_size=12,
            anchor_x="center",
            anchor_y="center",
            batch=batch
        )
        self._x_min = x
        self._x_max = x + w
        self._y_min = y
        self._y_max = y + h
        self._color = color
        self._hover = hover
        self._click = click
        self._toggle = toggle
        self._toggled = toggled

    def is_hovered(self: Self, x: int, y: int, click: bool) -> bool:
        """Detect hovering of the button.

        Args:
            x (int): x component of the mouse position.
            y (int): y component of the mouse position.
            click (bool): Set True if a click happened.
        Returns:
            bool: True if hovered, False otherwise.
        """
        if self._x_min <= x <= self._x_max and self._y_min <= y <= self._y_max:
            self._button.color = self._click if click else self._hover
            if self._toggle is not None and click:
                self._toggled = not self._toggled
            return True
        self._button.color = self._toggle if self._toggled else self._color
        return False

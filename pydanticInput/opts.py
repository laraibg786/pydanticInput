from __future__ import annotations

from functools import partial, wraps
from inspect import _empty, signature
from typing import TYPE_CHECKING

import PySide6.QtWidgets

if TYPE_CHECKING:
    import PySide6

def apply_funcs(obj, *funcs):
    for func in funcs:
        obj = func(obj)
    return obj


# https://stackoverflow.com/a/78149460
def curried(func):
    @wraps(func)
    def inner(*args, **kwds):
        new_f = partial(func, *args, **kwds)
        params = signature(new_f, follow_wrapped=True).parameters
        if all(params[p].default != _empty for p in params):
            return new_f()
        else:
            return curried(new_f)

    return inner


@curried
def with_layout(layout: PySide6.QtWidgets.QLayout, widget: PySide6.QtWidgets.QWidget) -> PySide6.QtWidgets.QWidget:
    widget.setLayout(layout)
    return widget


@curried
def with_window_title(title: str, widget: PySide6.QtWidgets.QWidget) -> PySide6.QtWidgets.QWidget:
    widget.setWindowTitle(title)
    return widget

@curried
def with_widgets(child_widgets: dict[str, PySide6.QtWidgets.QWidget], parent_widget: PySide6.QtWidgets.QWidget) -> PySide6.QtWidgets.QWidget:
    """
    Add child widgets to a parent widget.
    """
    for name, child in child_widgets.items():
        child.setParent(parent_widget)
        parent_widget.layout().addRow(name, child)
    return parent_widget

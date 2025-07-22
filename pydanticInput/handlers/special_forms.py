"""
Special forms are constructs in the typing module that have unique syntax or behavior.
According to the Python documentation, the following are considered special forms:

- typing.Union
- typing.Optional
- typing.Literal
- typing.Annotated

Reference: https://docs.python.org/3/library/typing.html#special-forms
"""

import typing

from pydantic import fields
from PySide6 import QtWidgets

import pydanticInput


def handle_union(field: fields.FieldInfo):
    """
    Creates a QWidget for handling Union types in a form, allowing the user to select among multiple types.

    Args:
        field (FieldInfo): The field information containing the Union annotation.

    Returns:
        Tuple[QWidget, Callable[[], Any]]:
            - The QWidget containing a combo box for type selection and a stacked widget for the corresponding input widgets.
            - A callable that returns the value from the currently selected widget.
    """
    container = QtWidgets.QWidget()
    type_selector = QtWidgets.QComboBox()
    stack = QtWidgets.QStackedWidget()

    type_selector.currentIndexChanged.connect(stack.setCurrentIndex)

    layout = QtWidgets.QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(type_selector)
    layout.addWidget(stack)

    union_types = typing.get_args(field.annotation)
    widget_mapping = dict(
        pydanticInput.type_dispatch(union_type)(
            fields.FieldInfo.from_annotation(union_type)
        )
        for union_type in union_types
    )
    for widget, t in zip(widget_mapping, union_types):
        type_selector.addItem(t.__name__ if hasattr(t, "__name__") else str(t))
        stack.addWidget(widget)

    return container, lambda: widget_mapping[stack.currentWidget()]()


def handle_literal(field: fields.FieldInfo):
    """
    Handle a Literal field to extract its properties.
    """
    value_map = {str(v): v for v in typing.get_args(field.annotation)}
    widget = QtWidgets.QComboBox()
    widget.addItems(value_map.keys())
    return widget, lambda: value_map[widget.currentText()]

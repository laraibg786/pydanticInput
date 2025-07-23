"""
Handlers for Python typing special forms (Union, Literal, etc.) for Qt forms.

Special forms are constructs in the typing module with unique syntax or
behavior, such as:
    - Union
    - Optional
    - Literal
    - Annotated

These handlers allow dynamic form generation for fields using these types in
Pydantic models. See:
https://docs.python.org/3/library/typing.html#special-forms
"""

import typing

from pydantic import fields
from PySide6 import QtWidgets

import pydanticInput


def handle_union(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QWidget, typing.Callable[[], typing.Any]]:
    """
    Create a QWidget for a Union field, letting the user select among types.

    Args:
        field (FieldInfo): The field info with a Union annotation.

    Returns:
        tuple[QWidget, Callable[[], Any]]: A tuple where:
            - QWidget contains a combo box for type selection and a stacked
              widget for the corresponding input widgets.
            - The callable returns the value from the currently selected widget.

    Notes:
        - Supports any Union of types supported by type_dispatch.
        - The widget updates dynamically as the user selects a type.
        - If a type in the Union is not supported, NotImplementedError is
          raised by type_dispatch.
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
    for widget, t in zip(widget_mapping, union_types, strict=True):
        type_selector.addItem(t.__name__ if hasattr(t, "__name__") else str(t))
        stack.addWidget(widget)

    return container, lambda: widget_mapping[stack.currentWidget()]()  # noqa: PLW0108


def handle_literal(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QComboBox, typing.Callable[[], typing.Any]]:
    """
    Create a QComboBox for a Literal field, letting the user select a value.

    Args:
        field (FieldInfo): The field info with a Literal annotation.

    Returns:
        tuple[QComboBox, Callable[[], Any]]: A tuple where:
            - QComboBox lets the user select among literal values.
            - The callable returns the selected literal value.

    Notes:
        - Only values explicitly listed in the Literal are allowed.
        - The widget always returns a value of the correct type.
    """
    value_map = {str(v): v for v in typing.get_args(field.annotation)}
    widget = QtWidgets.QComboBox()
    widget.addItems(value_map.keys())
    return widget, lambda: value_map[widget.currentText()]

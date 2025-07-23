import datetime
import decimal
import sys
import types
import typing
from enum import Enum

from pydantic import BaseModel, fields
from PySide6 import QtWidgets

from pydanticInput.handlers import pydantic_types, special_forms, std_types


T = typing.TypeVar("T")


class FieldHandler(typing.Protocol[T]):
    """
    Protocol for handler functions that create a QWidget for a field and
    provide a callable to retrieve the user input value.

    The handler takes a FieldInfo object and returns a tuple:
        - QWidget: The widget for user input.
        - Callable[[], T]: A function to get the value from the widget.
    """

    def __call__(
        self, field: fields.FieldInfo
    ) -> tuple[QtWidgets.QWidget, typing.Callable[[], T]]: ...


def type_dispatch(field_type: type | object) -> FieldHandler[typing.Any]:
    """
    Return a handler for the given field type to build a Qt input widget.

    This function inspects the provided type annotation or class and returns
    a handler function that can create a QWidget for user input and a callable
    to extract the value. Supported cases:

    - int: Uses a spinbox for integer input.
    - float, Decimal: Uses a double spinbox for numeric input.
    - str: Uses a line edit for string input.
    - bool: Uses a checkbox for boolean input.
    - datetime, date, time: Uses appropriate date/time widgets.
    - Enum: Uses a combo box for enum selection.
    - BaseModel: Recursively builds a form for nested models.
    - NoneType: Handles optional/nullable fields.
    - list: Uses a list widget for multiple values.
    - dict: Uses a dictionary editor widget.
    - Literal: Uses a combo box for literal choices.
    - Union: Allows switching between multiple types at runtime.

    Args:
        field_type (type | object): The type annotation or class to dispatch
            a handler for.

    Returns:
        FieldHandler[Any]: A handler function for the given type.

    Raises:
        NotImplementedError: If no handler is implemented for the provided
            type. This occurs for unsupported or custom types that do not
            match any of the above cases. The error message includes the
            unhandled type and suggests contributing a handler.

    Example:
        handler = type_dispatch(int)
        widget, getter = handler(field_info)
        # widget is a QSpinBox, getter returns the int value
    """

    origin_type = typing.get_origin(field_type)
    if origin_type is None and isinstance(field_type, type):
        if field_type is int:
            return std_types.handle_int

        elif field_type in {float, decimal.Decimal}:
            return std_types.handle_numeric

        elif field_type is str:
            return std_types.handle_str

        elif field_type is bool:
            return std_types.handle_bool

        elif field_type is datetime.datetime:
            return std_types.handle_datetime

        elif field_type is datetime.date:
            return std_types.handle_date

        elif field_type is datetime.time:
            return std_types.handle_time

        elif issubclass(field_type, Enum):
            return std_types.handle_enums

        elif issubclass(field_type, BaseModel):
            return pydantic_types.handle_BaseModel

        elif field_type is type(None):
            return std_types.handle_None

    elif origin_type is list:
        return std_types.handle_list

    elif origin_type is dict:
        return std_types.handle_dict

    elif origin_type is typing.Literal:
        return special_forms.handle_literal

    elif origin_type is typing.Union or (
        False
        if sys.version_info < (3, 10)
        else (origin_type is types.UnionType)
    ):
        return special_forms.handle_union

    raise NotImplementedError(
        f"Handler for type:: `{field_type}` is not yet implemented. "
        "Consider implementing yourself or better yet raise a PR."
    )

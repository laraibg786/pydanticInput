import datetime
import decimal
import sys
import types
import typing
from enum import Enum

from pydantic import BaseModel

from pydanticInput.handlers import pydantic_types, special_forms, std_types


def type_dispatch(field_type: type) -> typing.Callable:
    """
    Dispatches the appropriate handler function based on the provided field
    type. This function inspects the given `field_type` and returns a
    corresponding handler function for processing values of that type. It
    supports standard Python types (int, float, str, bool, etc.), datetime
    types, enums, Pydantic BaseModel subclasses, NoneType, as well as
    generic types such as list, dict, Literal, and Union. If the type is
    not recognized, a NotImplementedError is raised.

    Args:
        field_type (type): The type annotation or class to dispatch a handler
        for.

    Returns:
        Callable: A handler function suitable for processing values of the given
        type.

    Raises:
        NotImplementedError: If no handler is implemented for the provided type.
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

import datetime
import decimal
import sys
import types
import typing
from enum import Enum

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTimeEdit,
    QWidget,
)

from pydanticInput.widgets import ListEditWidget


def handle_BaseModel(model: BaseModel):
    """
    Handle a Pydantic BaseModel to extract its fields and types.
    """
    fields = {}
    for name, field in model.__pydantic_fields__.items():
        fields[name] = type_dispatch(field.annotation)(field)

    return fields


def type_dispatch(field_type):
    origin_type = typing.get_origin(field_type)
    if origin_type is None and isinstance(field_type, type):
        if field_type is int:
            return handle_int
        elif field_type is str:
            return handle_str
        elif field_type in (float, decimal.Decimal):
            return handle_numeric
        elif field_type is bool:
            return handle_bool
        elif field_type is datetime.datetime:
            return handle_datetime
        elif field_type is datetime.date:
            return handle_date
        elif field_type is datetime.time:
            return handle_time
        elif field_type is tuple:
            return ...
        elif field_type is dict:
            return ...
        elif field_type is set:
            return ...
        elif issubclass(field_type, Enum):
            return handle_enums
    elif origin_type is list:
        return handle_list
    elif origin_type is tuple:
        return ...
    elif origin_type is typing.Literal:
        return handle_literal
    elif origin_type is typing.Union or (
        False if sys.version_info < (3, 10) else (origin_type is types.UnionType)
    ):
        return handle_union
    else:
        raise NotImplementedError(
            f"Handler for type:: `{field_type}` is not yet implemented. "
            "Consider implementing yourself or better yet raise a PR."
        )


def handle_int(field: FieldInfo, range=(-(2**31), 2**31 - 1)):
    """
    Handle an integer field to extract its properties.
    """
    widget = QSpinBox()
    widget.setRange(*range)
    return widget, widget.value


def handle_numeric(field: FieldInfo, range=(-(2**31), 2**31 - 1)):
    """
    Handle a numeric field to extract its properties.
    """
    widget = QDoubleSpinBox()
    widget.setRange(*range)
    return widget, widget.value


def handle_str(field: FieldInfo):
    """
    Handle a string field to extract its properties.
    """
    widget = QLineEdit()
    return widget, widget.text


def handle_bool(field: FieldInfo):
    """
    Handle a boolean field to extract its properties.
    """
    widget = QCheckBox()
    return widget, widget.isChecked


def handle_datetime(field: FieldInfo):
    """Handle a datetime field to extract its properties."""
    widget = QDateTimeEdit()
    widget.setCalendarPopup(True)
    return widget, widget.dateTime().toPython


def handle_date(field: FieldInfo):
    """Handle a date field to extract its properties."""
    widget = QDateEdit()
    widget.setCalendarPopup(True)
    return widget, widget.date().toPython


def handle_list(field: FieldInfo):
    item_type = typing.get_args(field.annotation)[0]
    item_input_widget, item_getter = type_dispatch(item_type)(
        FieldInfo.from_annotation(item_type)
    )

    container = QWidget()
    list_widget = ListEditWidget()
    add_button = QPushButton("Add")
    layout = QGridLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)

    # Add widgets using grid positions
    layout.addWidget(list_widget, 0, 0, 1, 2)  # list_widget spans 2 columns
    layout.addWidget(item_input_widget, 1, 0)  # input field in left column
    layout.addWidget(add_button, 1, 1)  # button in right column

    add_button.clicked.connect(lambda: list_widget.add_value(item_getter()))
    return container, list_widget.get_values


def handle_time(field: FieldInfo):
    """Handle a time field to extract its properties."""
    widget = QTimeEdit()
    return widget, widget.time().toPython


def handle_enums(field: FieldInfo):
    """
    Handle an Enum field to extract its properties.
    """
    widget = QComboBox()
    widget.addItems([member.value for member in field.annotation])
    return widget, widget.currentText


def handle_literal(field: FieldInfo):
    """
    Handle a Literal field to extract its properties.
    """
    value_map = {str(v): v for v in typing.get_args(field.annotation)}
    widget = QComboBox()
    widget.addItems(value_map.keys())
    return widget, lambda: value_map[widget.currentText()]


def handle_union(field: FieldInfo):
    """
    Creates a QWidget for handling Union types in a form, allowing the user to select among multiple types.

    Args:
        field (FieldInfo): The field information containing the Union annotation.

    Returns:
        Tuple[QWidget, Callable[[], Any]]:
            - The QWidget containing a combo box for type selection and a stacked widget for the corresponding input widgets.
            - A callable that returns the value from the currently selected widget.
    """
    container = QWidget()
    type_selector = QComboBox()
    stack = QStackedWidget()

    type_selector.currentIndexChanged.connect(stack.setCurrentIndex)

    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(type_selector)
    layout.addWidget(stack)

    union_types = typing.get_args(field.annotation)
    widget_mapping = dict(
        type_dispatch(union_type)(FieldInfo.from_annotation(union_type))
        for union_type in union_types
    )
    for widget, t in zip(widget_mapping, union_types):
        type_selector.addItem(t.__name__ if hasattr(t, "__name__") else str(t))
        stack.addWidget(widget)

    return container, lambda: widget_mapping[stack.currentWidget()]()

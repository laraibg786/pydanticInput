import datetime
from decimal import Decimal
from enum import Enum
from typing import Literal, _GenericAlias, get_args, get_origin

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDoubleSpinBox,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
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
    if isinstance(field_type, type):
        if field_type is int:
            return handle_int
        elif field_type is str:
            return handler_str
        elif field_type in (float, Decimal):
            return handle_numeric
        elif field_type is bool:
            return handle_bool
        elif field_type is datetime.datetime:
            return handle_datetime
        elif field_type is datetime.date:
            return handle_date
        elif field_type is datetime.time:
            return handle_time
        elif get_origin(field_type) is list:
            return handle_list
        elif field_type is tuple:
            return ...
        elif field_type is dict:
            return ...
        elif field_type is set:
            return ...
        elif issubclass(field_type, Enum):
            return handle_enums
    elif isinstance(field_type, _GenericAlias):
        if get_origin(field_type) is list:
            return handle_list
        elif get_origin(field_type) is tuple:
            return ...
        elif get_origin(field_type) is Literal:
            return handle_literal
    else:
        raise NotImplementedError(
            f"Handler for type:: {field_type} is not yet implemented."
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


def handler_str(field: FieldInfo):
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
    item_type = get_args(field.annotation)[0]
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
    value_map = {str(v): v for v in get_args(field.annotation)}
    widget = QComboBox()
    widget.addItems(value_map.keys())
    return widget, lambda: value_map[widget.currentText()]

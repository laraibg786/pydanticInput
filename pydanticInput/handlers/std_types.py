import datetime
import typing

from pydantic import fields
from PySide6 import QtWidgets

import pydanticInput
from pydanticInput.widgets import DictEditWidget, ListEditWidget


# primative types


def handle_int(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QSpinBox, typing.Callable[[], int]]:
    """
    Handle an integer field to extract its properties.

    Returns:
        A tuple containing a QSpinBox widget and a callable that returns the
        current integer value.
    """
    widget = QtWidgets.QSpinBox()
    widget.setRange(-(2**31), 2**31 - 1)
    return widget, widget.value


def handle_numeric(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QDoubleSpinBox, typing.Callable[[], float]]:
    """
    Handle a numeric field to extract its properties.

    Returns:
        A tuple containing a QDoubleSpinBox widget and a callable that returns
        the current float value.
    """
    widget = QtWidgets.QDoubleSpinBox()
    widget.setRange(-(2**31), 2**31 - 1)
    return widget, widget.value


def handle_str(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QLineEdit, typing.Callable[[], str]]:
    """
    Handle a string field to extract its properties.

    Returns:
        A tuple containing a QLineEdit widget and a callable that returns
        the current string value.
    """
    widget = QtWidgets.QLineEdit()
    return widget, widget.text


def handle_bool(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QCheckBox, typing.Callable[[], bool]]:
    """
    Handle a boolean field to extract its properties.

    Returns:
        A tuple containing a QCheckBox widget and a callable that returns
        the current boolean value.
    """
    widget = QtWidgets.QCheckBox()
    return widget, widget.isChecked


def handle_None(  # noqa: N802
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QWidget, typing.Callable[[], None]]:
    """
    Handle a None field, which is typically used for optional fields.

    Returns:
        A tuple containing a QWidget and a callable that always returns None.
    """
    return QtWidgets.QWidget(), lambda: None


# non primative types


def handle_list(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QWidget, typing.Callable[[], list[object]]]:
    item_type = typing.get_args(field.annotation)[0]
    item_input_widget, item_getter = pydanticInput.type_dispatch(item_type)(
        fields.FieldInfo.from_annotation(item_type)
    )

    container = QtWidgets.QWidget()
    list_widget = ListEditWidget()
    add_button = QtWidgets.QPushButton("Add")
    layout = QtWidgets.QGridLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)

    # Add widgets using grid positions
    layout.addWidget(list_widget, 0, 0, 1, 2)  # list_widget spans 2 columns
    layout.addWidget(item_input_widget, 1, 0)  # input field in left column
    layout.addWidget(add_button, 1, 1)  # button in right column

    add_button.clicked.connect(lambda: list_widget.add_value(item_getter()))
    return container, list_widget.get_values


def handle_dict(
    field: fields.FieldInfo,
) -> tuple[
    QtWidgets.QWidget, typing.Callable[[], dict[typing.Hashable, object]]
]:
    """
    Creates a QWidget for editing dictionary fields, with dynamic key and value
    input widgets.

    Args:
        field (fields.FieldInfo): The field information containing the
        dictionary type annotation.

    Returns:
        tuple[QtWidgets.QWidget, Callable[[], dict[typing.Hashable, object]]]:
            - A QWidget containing the dictionary editor UI.
            - A callable that returns the current dictionary as entered by the
            user.
    The widget allows users to add key-value pairs using dynamically generated
    input widgets for the specified key and value types. The returned callable
    retrieves the current state of the dictionary from the UI.
    """

    key_type, value_type = typing.get_args(field.annotation)
    key_widget, key_getter = pydanticInput.type_dispatch(key_type)(
        fields.FieldInfo.from_annotation(key_type)
    )
    value_widget, value_getter = pydanticInput.type_dispatch(value_type)(
        fields.FieldInfo.from_annotation(value_type)
    )

    container = QtWidgets.QWidget()
    dict_widget = DictEditWidget()
    add_button = QtWidgets.QPushButton("Add")

    layout = QtWidgets.QGridLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(dict_widget, 0, 0, 1, 3)
    layout.addWidget(key_widget, 1, 0)
    layout.addWidget(value_widget, 1, 1)
    layout.addWidget(add_button, 1, 2)

    add_button.clicked.connect(
        lambda: dict_widget.add_pair(key_getter(), value_getter())
    )
    return container, dict_widget.get_dict


# datetime types


def handle_datetime(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QDateTimeEdit, typing.Callable[[], datetime.datetime]]:
    """
    Handle a datetime field to extract its properties.

    Returns:
        A tuple containing a QDateTimeEdit widget and a callable that returns
        the current datetime value.
    """
    widget = QtWidgets.QDateTimeEdit()
    widget.setCalendarPopup(True)
    return widget, widget.dateTime().toPython


def handle_date(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QDateEdit, typing.Callable[[], datetime.date]]:
    """
    Handle a date field to extract its properties.

    Returns:
        A tuple containing a QDateEdit widget and a callable that returns
        the current date value.
    """
    widget = QtWidgets.QDateEdit()
    widget.setCalendarPopup(True)
    return widget, widget.date().toPython


def handle_time(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QTimeEdit, typing.Callable[[], datetime.time]]:
    """
    Handle a time field to extract its properties.

    Returns:
        A tuple containing a QTimeEdit widget and a callable that returns
        the current time value.
    """
    widget = QtWidgets.QTimeEdit()
    return widget, widget.time().toPython


# enums


def handle_enums(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QComboBox, typing.Callable[[], str]]:
    """
    Handle an Enum field to extract its properties.

    Returns:
        A tuple containing a QComboBox widget and a callable that returns
        the current selected text as a string.
    """
    widget = QtWidgets.QComboBox()
    widget.addItems([member.value for member in field.annotation])
    return widget, widget.currentText

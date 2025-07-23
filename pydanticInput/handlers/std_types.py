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
    Create a QSpinBox for an integer field and a callable to get its value.

    Args:
        field (FieldInfo): The field info for the int field.

    Returns:
        tuple[QSpinBox, Callable[[], int]]: A tuple where:
            - QSpinBox: The widget for integer input.
            - Callable[[], int]: Returns the current integer value from the
              widget.
    """
    widget = QtWidgets.QSpinBox()
    widget.setRange(-(2**31), 2**31 - 1)
    return widget, widget.value


def handle_numeric(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QDoubleSpinBox, typing.Callable[[], float]]:
    """
    Create a QDoubleSpinBox for a float/Decimal field and a callable to get
    its value.

    Args:
        field (FieldInfo): The field info for the numeric field.

    Returns:
        tuple[QDoubleSpinBox, Callable[[], float]]: A tuple where:
            - QDoubleSpinBox: The widget for float/decimal input.
            - Callable[[], float]: Returns the current float value from the
              widget.
    """
    widget = QtWidgets.QDoubleSpinBox()
    widget.setRange(-(2**31), 2**31 - 1)
    return widget, widget.value


def handle_str(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QLineEdit, typing.Callable[[], str]]:
    """
    Create a QLineEdit for a string field and a callable to get its value.

    Args:
        field (FieldInfo): The field info for the str field.

    Returns:
        tuple[QLineEdit, Callable[[], str]]: A tuple where:
            - QLineEdit: The widget for string input.
            - Callable[[], str]: Returns the current string value from the
              widget.
    """
    widget = QtWidgets.QLineEdit()
    return widget, widget.text


def handle_bool(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QCheckBox, typing.Callable[[], bool]]:
    """
    Create a QCheckBox for a boolean field and a callable to get its value.

    Args:
        field (FieldInfo): The field info for the bool field.

    Returns:
        tuple[QCheckBox, Callable[[], bool]]: A tuple where:
            - QCheckBox: The widget for boolean input.
            - Callable[[], bool]: Returns the current boolean value from the
              widget.
    """
    widget = QtWidgets.QCheckBox()
    return widget, widget.isChecked


def handle_None(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QWidget, typing.Callable[[], None]]:
    """
    Create a QWidget for a None field (optional/nullable) and a callable
    that always returns None.

    Args:
        field (FieldInfo): The field info for the None field.

    Returns:
        tuple[QWidget, Callable[[], None]]: A tuple where:
            - QWidget: The widget for None/optional input (empty widget).
            - Callable[[], None]: Always returns None.
    """
    return QtWidgets.QWidget(), lambda: None


# non primative types


def handle_list(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QWidget, typing.Callable[[], list[object]]]:
    """
    Create a QWidget for a list field and a callable to get its values.

    Args:
        field (FieldInfo): The field info for the list field.

    Returns:
        tuple[QWidget, Callable[[], list[object]]]: A tuple where:
            - QWidget: The widget for list input (with add/remove support).
            - Callable[[], list[object]]: Returns the current list of values
              from the widget.

    Notes:
        - The widget allows adding items of the specified type.
        - If the item type is not supported, NotImplementedError is raised by
          type_dispatch.
    """
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
    Create a QWidget for a dict field and a callable to get its value.

    Args:
        field (FieldInfo): The field info for the dict field.

    Returns:
        tuple[QWidget, Callable[[], dict[Hashable, object]]]: A tuple where:
            - QWidget: The widget for dictionary input (with add/remove
              support).
            - Callable[[], dict[Hashable, object]]: Returns the current
              dictionary as entered by the user.

    Notes:
        - The widget allows users to add key-value pairs using dynamically
          generated input widgets for the specified key and value types.
        - The returned callable retrieves the current state of the dictionary
          from the UI.
        - If the key or value type is not supported, NotImplementedError is
          raised by type_dispatch.
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
    Create a QDateTimeEdit for a datetime field and a callable to get its
    value.

    Args:
        field (FieldInfo): The field info for the datetime field.

    Returns:
        tuple[QDateTimeEdit, Callable[[], datetime]]: A tuple where:
            - QDateTimeEdit: The widget for datetime input.
            - Callable[[], datetime]: Returns the current datetime value from
              the widget.
    """
    widget = QtWidgets.QDateTimeEdit()
    widget.setCalendarPopup(True)
    return widget, widget.dateTime().toPython


def handle_date(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QDateEdit, typing.Callable[[], datetime.date]]:
    """
    Create a QDateEdit for a date field and a callable to get its value.

    Args:
        field (FieldInfo): The field info for the date field.

    Returns:
        tuple[QDateEdit, Callable[[], date]]: A tuple where:
            - QDateEdit: The widget for date input.
            - Callable[[], date]: Returns the current date value from the
              widget.
    """
    widget = QtWidgets.QDateEdit()
    widget.setCalendarPopup(True)
    return widget, widget.date().toPython


def handle_time(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QTimeEdit, typing.Callable[[], datetime.time]]:
    """
    Create a QTimeEdit for a time field and a callable to get its value.

    Args:
        field (FieldInfo): The field info for the time field.

    Returns:
        tuple[QTimeEdit, Callable[[], time]]: A tuple where:
            - QTimeEdit: The widget for time input.
            - Callable[[], time]: Returns the current time value from the
              widget.
    """
    widget = QtWidgets.QTimeEdit()
    return widget, widget.time().toPython


# enums


def handle_enums(
    field: fields.FieldInfo,
) -> tuple[QtWidgets.QComboBox, typing.Callable[[], str]]:
    """
    Create a QComboBox for an Enum field and a callable to get its value.

    Args:
        field (FieldInfo): The field info for the Enum field.

    Returns:
        tuple[QComboBox, Callable[[], str]]: A tuple where:
            - QComboBox: The widget for enum selection.
            - Callable[[], str]: Returns the current selected text as a
              string.
    """
    widget = QtWidgets.QComboBox()
    widget.addItems([member.value for member in field.annotation])
    return widget, widget.currentText

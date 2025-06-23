from enum import Enum

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from PySide6.QtWidgets import QCheckBox, QDoubleSpinBox, QLineEdit, QSpinBox, QWidget

from pydanticInput.opts import apply_funcs, with_layout, with_widgets


def handle_BaseModel(model: BaseModel):
    """
    Handle a Pydantic BaseModel to extract its fields and types.
    """
    fields = {}
    for name, field in model.__pydantic_fields__.items():
        field_annotations = field.annotation
        if isinstance(field_annotations, type):
            if issubclass(field_annotations, BaseModel):
                fields[name] = handle_BaseModel(field_annotations)
            elif field_annotations is int:
                fields[name] = handle_int(field)
            elif field_annotations is str:
                fields[name] = handler_str(field)
            elif field_annotations is float:
                fields[name] = handle_numeric(field)
            elif field_annotations is bool:
                fields[name] = "bool"
            elif field_annotations is list:
                fields[name] = "list"
            elif field_annotations is dict:
                fields[name] = "dict"
            elif field_annotations is set:
                fields[name] = "set"
            elif field_annotations is tuple:
                fields[name] = "tuple"
            if issubclass(field_annotations, Enum):
                fields[name] = field_annotations
        else:
            fields[name] = (
                field_annotations.__name__
                if hasattr(field_annotations, "__name__")
                else str(field_annotations)
            )

    return fields


def handle_int(FieldInfo: FieldInfo, range=(-(2**31), 2**31 - 1)) -> QWidget:
    """
    Handle an integer field to extract its properties.
    """
    widget = QSpinBox()
    widget.setRange(*range)
    return widget, widget.value


def handle_numeric(FieldInfo: FieldInfo, range=(-(2**31), 2**31 - 1)) -> QWidget:
    """
    Handle a numeric field to extract its properties.
    """
    widget = QDoubleSpinBox()
    widget.setRange(*range)
    return widget, widget.value


def handler_str(FieldInfo: FieldInfo) -> QWidget:
    """
    Handle a string field to extract its properties.
    """
    widget = QLineEdit()
    return widget, widget.text


def handle_bool(FieldInfo: FieldInfo) -> QWidget:
    """
    Handle a boolean field to extract its properties.
    """
    widget = QCheckBox()
    return widget, widget.isChecked

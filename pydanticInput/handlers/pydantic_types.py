import typing

import pydantic
from pydantic import fields
from PySide6 import QtWidgets

import pydanticInput


def handle_BaseModel(
    model: typing.Union[pydantic.BaseModel, fields.FieldInfo],
):
    """
    Handle a Pydantic BaseModel to extract its fields and types.
    """
    fields_container = QtWidgets.QWidget()
    fields_container.setLayout(QtWidgets.QFormLayout())
    fields_container.layout().setContentsMargins(0, 0, 0, 0)

    if isinstance(model, fields.FieldInfo):
        output_widget = QtWidgets.QWidget()
        output_widget.setLayout(QtWidgets.QVBoxLayout())
        output_widget.layout().setContentsMargins(0, 0, 0, 0)
        cb = QtWidgets.QCheckBox("show input widget")
        output_widget.layout().addWidget(cb)
        output_widget.layout().addWidget(fields_container)
        cb.toggled.connect(fields_container.setVisible)
        fields_container.setVisible(cb.isChecked())
        model = model.annotation
    else:
        output_widget = fields_container

    field_val_map = {}
    for field_name, field in model.__pydantic_fields__.items():
        field_widget, field_getter = pydanticInput.type_dispatch(field.annotation)(
            field
        )
        fields_container.layout().addRow(field_name, field_widget)
        field_val_map[field_name] = field_getter

    return output_widget, lambda: {
        field_name: getter() for field_name, getter in field_val_map.items()
    }

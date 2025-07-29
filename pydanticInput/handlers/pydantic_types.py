import typing

import pydantic
from pydantic import fields
from PySide6 import QtWidgets

import pydanticInput


def handle_BaseModel(
    model: type[pydantic.BaseModel] | fields.FieldInfo,
) -> tuple[QtWidgets.QWidget, typing.Callable[[], dict]]:
    """
    Create a QWidget form for a Pydantic BaseModel and a callable to get input.

    Args:
        model (type[BaseModel] | FieldInfo):
            The Pydantic model class or a FieldInfo object with the model
            annotation.

    Returns:
        tuple[QWidget, Callable[[], dict]]: A tuple where:
            - The QWidget contains the form for the model fields.
            - The callable returns a dict mapping field names to user input.

    Notes:
        - If a FieldInfo is provided, a checkbox is included to show or hide
          the input widget.
        - Nested types (BaseModel fields) are also handled recursively.
    """
    field_container_layout = QtWidgets.QFormLayout()
    is_field_info = isinstance(model, fields.FieldInfo)

    if is_field_info:
        field_dialog = QtWidgets.QDialog()
        field_dialog.setLayout(field_container_layout)
        model = model.annotation
        output_widget = QtWidgets.QPushButton("open the dialog")
        output_widget.clicked.connect(lambda: field_dialog.exec())  # noqa: PLW0108
    else:
        fields_container = QtWidgets.QWidget()
        fields_container.setLayout(field_container_layout)
        fields_container.layout().setContentsMargins(0, 0, 0, 0)
        output_widget = fields_container

    field_val_map = {}
    for field_name, field in model.__pydantic_fields__.items():
        field_widget, field_getter = pydanticInput.type_dispatch(
            field.annotation
        )(field)
        field_container_layout.addRow(field_name, field_widget)
        field_val_map[field_name] = field_getter

    if is_field_info:
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        )
        field_container_layout.addWidget(btn_box)
        btn_box.accepted.connect(field_dialog.accept)

    return output_widget, lambda: {
        field_name: getter() for field_name, getter in field_val_map.items()
    }

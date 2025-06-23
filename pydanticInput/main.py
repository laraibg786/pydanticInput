from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING
from pydanticInput.handlers import handle_BaseModel
from pydanticInput.opts import apply_funcs, with_layout, with_widgets, with_window_title

from PySide6.QtWidgets import QApplication, QDialog, QFormLayout, QDialogButtonBox

if TYPE_CHECKING:
    from pydantic import BaseModel


def Input(model: BaseModel):
    QApplication([])
    mapping_dict = handle_BaseModel(model)
    input_dialog = apply_funcs(
        QDialog(),
        with_layout(QFormLayout()),
        with_window_title("Input Dialog"),
        with_widgets({name: widget_pair[0] for name, widget_pair in mapping_dict.items()}),
    )
    input_dialog.layout().addWidget(QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel))
    input_dialog.exec()

    return {}

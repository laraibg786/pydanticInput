from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QApplication,
    QDialogButtonBox,
    QScrollArea,
)

from pydanticInput.handlers import handle_BaseModel

if TYPE_CHECKING:
    from pydantic import BaseModel


def Input(model: BaseModel):
    vals = {}
    app = QApplication([])
    widget, getter = handle_BaseModel(model)
    btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    btns.accepted.connect(lambda: vals.update(getter()))
    btns.accepted.connect(app.quit)
    btns.rejected.connect(app.quit)
    widget.layout().addWidget(btns)
    scroll_area = QScrollArea()
    scroll_area.setWidget(widget)
    scroll_area.show()
    app.exec()
    return vals

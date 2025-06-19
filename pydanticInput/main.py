from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication, QWidget

if TYPE_CHECKING:
    from pydantic import BaseModel


def Input(model: BaseModel):
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("My First PySide6 App")
    # window.resize(400, 300)
    window.show()

    # Start the event loop
    return {}, app.exec()


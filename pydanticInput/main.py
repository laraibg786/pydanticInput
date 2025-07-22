import pydantic
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QScrollArea

import pydanticInput


def Input(model: pydantic.BaseModel):
    vals = {}
    app = QApplication([])
    widget, getter = pydanticInput.type_dispatch(model)(model)
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

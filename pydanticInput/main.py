import pydantic
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QScrollArea

import pydanticInput


def Input(model: type[pydantic.BaseModel]) -> dict:
    """
    Display a PySide6 form for a Pydantic model and return user input as a dict.

    Args:
        model (type[BaseModel]): The Pydantic model class to generate the
            input form for.

    Returns:
        dict: A dictionary with values entered by the user, keyed by the
            model's fields.

    Notes:
        - The function blocks until the user closes the form.
        - The form includes OK and Cancel buttons.
        - On OK, input values are collected and returned.
        - On Cancel or window close, an empty dictionary is returned.
    """

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

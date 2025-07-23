import pydantic
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QScrollArea

import pydanticInput


def Input(model: pydantic.BaseModel) -> dict:  # noqa: N802
    """
    Displays a GUI form for a given Pydantic model and returns user input as a
    dictionary.

    Args:
        model (pydantic.BaseModel): The Pydantic model class to generate the
        input form for.

    Returns:
        dict: A dictionary containing the values entered by the user,
        corresponding to the model's fields.

    Notes:
        - The function creates a Qt application and displays a form based on the
        provided Pydantic model.
        - The form includes OK and Cancel buttons. On OK, the input values are
        collected and returned.
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

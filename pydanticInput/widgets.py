import ast
import typing

from PySide6 import QtCore, QtWidgets


class ListEditWidget(QtWidgets.QListWidget):
    """
    A QListWidget for editing lists with add/remove and drag-and-drop support.

    This widget allows users to add, remove, and reorder items in a list.
    Items are displayed with visual separators for clarity. Right-clicking
    an item opens a context menu to remove it. Items can be added
    programmatically using `add_value`.

    Intended for use in dynamic forms for Pydantic models with list fields.
    """

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.setSelectionMode(QtWidgets.QListWidget.SingleSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QListWidget.InternalMove)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Style items with border and padding for clear visual separation
        self.setStyleSheet("""
            QListWidget::item {
                border: 1px solid gray;
                border-radius: 4px;
                padding: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #a8d8ff;
                border-color: #1a73e8;
            }
        """)

    def _show_context_menu(self, position: QtCore.QPoint):
        """
        Show a context menu at the given position to remove the selected item.

        Args:
            position (QPoint): The position where the menu should appear.
        """
        menu = QtWidgets.QMenu()
        remove_action = menu.addAction("Remove")
        action = menu.exec(self.mapToGlobal(position))
        if action == remove_action:
            item = self.currentItem()
            if item:
                self.takeItem(self.row(item))

    def add_value(self, item: object) -> None:
        """
        Add an item to the list.

        Args:
            item (object): The item to add. Supports any type that can be
                represented as a string and reconstructed with ast.literal_eval.

        Notes:
            - Items are stored as their string representation.
            - Non-literal types or objects that cannot be reconstructed with
              ast.literal_eval may not be supported.
        """
        self.addItem(repr(item))

    def get_values(self) -> list[object]:
        """
        Get all values in the list, reconstructed from their string
        representations.

        Returns:
            list[object]: A list of values, each reconstructed using
                ast.literal_eval from the string representation stored in the
                widget.

        Notes:
            - If an item cannot be reconstructed, an exception will be raised.
        """
        return [
            ast.literal_eval(self.item(i).text()) for i in range(self.count())
        ]


class DictEditWidget(QtWidgets.QTableWidget):
    """
    A QTableWidget for editing dictionaries with key-value pairs.

    This widget allows users to add and remove key-value pairs. Keys must be
    hashable and unique. Right-clicking a row opens a context menu to remove
    the selected row. Intended for use in dynamic forms for Pydantic models
    with dict fields.
    """

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(0, 2, parent)
        self.setHorizontalHeaderLabels(["Key", "Value"])
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.__keys = set()

    def _show_context_menu(self, position: QtCore.QPoint):
        """
        Show a context menu at the given position to remove selected rows.

        Args:
            position (QPoint): The position where the menu should appear.
        """
        menu = QtWidgets.QMenu()
        remove_action = menu.addAction("Remove Selected Row")
        action = menu.exec(self.viewport().mapToGlobal(position))
        if action == remove_action:
            for row in sorted(
                set(index.row() for index in self.selectedIndexes()),
                reverse=True,
            ):
                self.removeRow(row)

    def add_pair(self, key: typing.Hashable, value: object) -> None:
        """
        Add a key-value pair to the table if the key is hashable and unique.

        Args:
            key (Hashable): The key to add. Must be hashable and unique.
            value (object): The value to add.

        Notes:
            - If the key is not hashable or already exists, the pair is not
              added.
        """
        try:
            if key in self.__keys:
                print(
                    f"warning:: ignoring key:: `{key}` is for exisitng already."
                )
                return
            self.__keys.add(key)
        except TypeError:
            print(
                f"warning:: the key of type `{type(key)}` is not hashable."
                " Discarding."
            )
            return
        row_position = self.rowCount()
        self.insertRow(row_position)
        self.setItem(row_position, 0, QtWidgets.QTableWidgetItem(repr(key)))
        self.setItem(row_position, 1, QtWidgets.QTableWidgetItem(repr(value)))

    def get_dict(self) -> dict[typing.Hashable, object]:
        """
        Get the current dictionary from the table, reconstructing keys and
        values.

        Returns:
            dict[Hashable, object]: The current dictionary, with keys and values
                reconstructed using ast.literal_eval from their string
                representations.

        Notes:
            - If a key or value cannot be reconstructed, that pair is skipped.
        """
        result = {}
        for row in range(self.rowCount()):
            key_item = self.item(row, 0)
            value_item = self.item(row, 1)
            if key_item and value_item:
                try:
                    result[ast.literal_eval(key_item.text())] = (
                        ast.literal_eval(value_item.text())
                    )
                except (SyntaxError, NameError, TypeError, ValueError) as e:
                    print(
                        "warning:: encounterd the error for converting: "
                        f"key = {key_item.text()} | value = {value_item.text()}"
                        f"\nexception :: {e}"
                    )
                    continue
        return result

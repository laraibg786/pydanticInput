import typing

from PySide6 import QtCore, QtWidgets


class ListEditWidget(QtWidgets.QListWidget):
    """
    Custom QListWidget with right-click removal support and
    a simple method to add items programmatically.
    Displays items with visual separators.
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
        menu = QtWidgets.QMenu()
        remove_action = menu.addAction("Remove")
        action = menu.exec(self.mapToGlobal(position))
        if action == remove_action:
            item = self.currentItem()
            if item:
                self.takeItem(self.row(item))

    def add_value(self, item: object) -> None:
        """
        Add an item to the list. Supports basic types.
        """
        self.addItem(repr(item))

    def get_values(self) -> list[object]:
        """
        Return all values in the list as strings.

        Returns:
            list: A list of values (as reconstructed from their string
            representations).
        """
        return [eval(self.item(i).text()) for i in range(self.count())]


class DictEditWidget(QtWidgets.QTableWidget):
    """
    A widget to allow editing a dictionary with key-value pairs using
    QTableWidget.
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
        result = {}
        for row in range(self.rowCount()):
            key_item = self.item(row, 0)
            value_item = self.item(row, 1)
            if key_item and value_item:
                try:
                    result[eval(key_item.text())] = eval(value_item.text())
                except (SyntaxError, NameError, TypeError, ValueError) as e:
                    print(
                        "warning:: encounterd the error for converting: "
                        f"key = {key_item.text()} | value = {value_item.text()}"
                        f"\nexception :: {e}"
                    )
                    continue
        return result

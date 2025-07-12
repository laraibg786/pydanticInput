from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QListWidget,
    QMenu,
    QTableWidget,
    QTableWidgetItem,
)


class ListEditWidget(QListWidget):
    """
    Custom QListWidget with right-click removal support and
    a simple method to add items programmatically.
    Displays items with visual separators.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
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

    def _show_context_menu(self, position):
        menu = QMenu()
        remove_action = menu.addAction("Remove")
        action = menu.exec(self.mapToGlobal(position))
        if action == remove_action:
            item = self.currentItem()
            if item:
                self.takeItem(self.row(item))

    def add_value(self, item):
        """
        Add an item to the list. Supports basic types.
        """
        self.addItem(repr(item))

    def get_values(self):
        """
        Return all values in the list as strings.
        """
        return [eval(self.item(i).text()) for i in range(self.count())]


class DictEditWidget(QTableWidget):
    """
    A widget to allow editing a dictionary with key-value pairs using QTableWidget.
    """

    def __init__(self, parent=None):
        super().__init__(0, 2, parent)
        self.setHorizontalHeaderLabels(["Key", "Value"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

        self.__keys = set()

    def _show_context_menu(self, position):
        menu = QMenu()
        remove_action = menu.addAction("Remove Selected Row")
        action = menu.exec(self.viewport().mapToGlobal(position))
        if action == remove_action:
            for row in sorted(
                set(index.row() for index in self.selectedIndexes()), reverse=True
            ):
                self.removeRow(row)

    def add_pair(self, key, value):
        try:
            if key in self.__keys:
                print(f"warning:: ignoring key:: `{key}` is for exisitng already.")
                return
            self.__keys.add(key)
        except TypeError:
            print(
                f"warning:: the key of type `{type(key)}` is not hashable. Discarding."
            )
            return
        row_position = self.rowCount()
        self.insertRow(row_position)
        self.setItem(row_position, 0, QTableWidgetItem(repr(key)))
        self.setItem(row_position, 1, QTableWidgetItem(repr(value)))

    def get_dict(self):
        result = {}
        for row in range(self.rowCount()):
            key_item = self.item(row, 0)
            value_item = self.item(row, 1)
            if key_item and value_item:
                try:
                    result[eval(key_item.text())] = eval(value_item.text())
                except Exception as e:
                    print(
                        "warning:: encounterd the error for converting: "
                        f"key = {key_item.text()} :: value = {value_item.text()}\n"
                        f"exception :: {e}"
                    )
                    continue
        return result

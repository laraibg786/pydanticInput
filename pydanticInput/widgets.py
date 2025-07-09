from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QMenu


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

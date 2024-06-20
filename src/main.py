from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, pyqtProperty
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (
    QWidget,
)


class NewTyper(QWidget):
    def __init__(
        self, parent: QWidget | None = ..., flags: Qt.WindowFlags | Qt.WindowType = ...
    ) -> None:
        super().__init__()
        self.init_ui()

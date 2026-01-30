from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import FluentIcon as FIF


def build_cell(icon: FIF) -> QWidget:
    icon_label = QLabel()
    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    icon_label.setFixedSize(48, 48)
    icon_label.setPixmap(icon.icon().pixmap(24, 24))

    text_label = QLabel(icon.name)
    text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    text_label.setWordWrap(True)
    text_label.setStyleSheet("color: #334155; font-size: 11px;")

    cell = QWidget()
    layout = QVBoxLayout(cell)
    layout.setContentsMargins(6, 6, 6, 6)
    layout.setSpacing(6)
    layout.addWidget(icon_label)
    layout.addWidget(text_label)
    return cell


def main() -> None:
    app = QApplication([])
    app.setFont(QFont("Fira Sans", 9))

    grid = QGridLayout()
    grid.setSpacing(12)

    icons = list(FIF)
    columns = 8
    for idx, icon in enumerate(icons):
        row = idx // columns
        col = idx % columns
        grid.addWidget(build_cell(icon), row, col)

    container = QWidget()
    container.setLayout(grid)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(container)

    window = QWidget()
    window.setWindowTitle("FluentIcon 图标画廊")
    window.resize(1100, 800)
    layout = QVBoxLayout(window)
    layout.addWidget(scroll)

    window.show()
    app.exec()


if __name__ == "__main__":
    main()

import sys

from PyQt6.QtWidgets import QApplication

from modules.ui.main_window import MainWindow
from modules.ui.style import apply_style


def main() -> int:
    app = QApplication(sys.argv)
    apply_style(app)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

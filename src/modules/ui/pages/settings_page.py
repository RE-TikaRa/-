from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from modules.app_state import AppState


class SettingsPage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setObjectName("settings")

        title = QLabel("系统设置")
        title.setObjectName("pageTitle")

        desc = QLabel("此页面用于后续扩展（用户、权限、系统参数等）。")

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addStretch(1)

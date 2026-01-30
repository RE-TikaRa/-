from PyQt6.QtWidgets import QLabel, QGridLayout, QVBoxLayout, QWidget, QFrame
from qfluentwidgets import SwitchButton, FluentIcon as FIF

from modules.app_state import AppState
from modules.simulator import Simulator


DEVICE_NAMES = {
    "oil_pump": "油泵",
    "cool_fan": "冷风机",
    "atomizer": "雾化器",
    "blower": "鼓风机",
    "induced_fan": "引风机",
    "heater": "加热",
    "feed_valve": "料泵阀门",
    "feed_pump": "加料泵",
    "dust_cleaner": "清灰",
    "air_hammer": "气锤",
    "discharge_fan": "关风机",
}

DEVICE_ICONS = {
    "oil_pump": FIF.POWER_BUTTON,
    "cool_fan": FIF.SPEED_HIGH,
    "atomizer": FIF.CLOUD,
    "blower": FIF.SPEED_MEDIUM,
    "induced_fan": FIF.SPEED_HIGH,
    "heater": FIF.BRIGHTNESS,
    "feed_valve": FIF.FILTER,
    "feed_pump": FIF.POWER_BUTTON,
    "dust_cleaner": FIF.BROOM,
    "air_hammer": FIF.ERASE_TOOL,
    "discharge_fan": FIF.SPEED_MEDIUM,
}


class OperationPage(QWidget):
    def __init__(self, state: AppState, sim: Simulator) -> None:
        super().__init__()
        self.state = state
        self.sim = sim
        self.setObjectName("operation")
        self._switches = {}
        self._status_dots = {}

        title = QLabel("操作界面")
        title.setObjectName("pageTitle")

        self.tip = QLabel("")
        self.tip.setProperty("class", "muted")

        grid = QGridLayout()
        row = 0
        for key, name in DEVICE_NAMES.items():
            icon = QLabel()
            icon.setFixedSize(18, 18)
            icon.setPixmap(DEVICE_ICONS[key].icon().pixmap(16, 16))

            label = QLabel(name)
            status = QLabel(" ")
            status.setFixedSize(12, 12)
            status.setStyleSheet("border-radius: 6px; background: #94A3B8;")

            switch = SwitchButton("启停")
            switch.setChecked(self.state.devices[key].is_on)
            switch.checkedChanged.connect(lambda checked, k=key: self._on_toggle(k, checked))

            self._switches[key] = switch
            self._status_dots[key] = status

            grid.addWidget(icon, row, 0)
            grid.addWidget(status, row, 1)
            grid.addWidget(label, row, 2)
            grid.addWidget(switch, row, 3)
            row += 1

        panel = QFrame()
        panel.setProperty("class", "card")
        panel_layout = QVBoxLayout(panel)
        panel_layout.addLayout(grid)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(panel)
        layout.addWidget(self.tip)
        layout.addStretch(1)

        self.sim.updated.connect(self._sync)
        self._sync()

    def _on_toggle(self, key: str, checked: bool) -> None:
        reason = self.sim.toggle_device(key, checked)
        if reason:
            self.tip.setText(f"{DEVICE_NAMES[key]}：{reason}")
        else:
            self.tip.setText("")

    def _sync(self) -> None:
        for key, device in self.state.devices.items():
            if key not in self._switches:
                continue
            self._switches[key].setChecked(device.is_on)
            color = "#22C55E" if device.is_on else "#94A3B8"
            self._status_dots[key].setStyleSheet(
                f"border-radius: 6px; background: {color};"
            )

from PyQt6.QtWidgets import QDoubleSpinBox, QFormLayout, QLabel, QVBoxLayout, QWidget, QGroupBox
from qfluentwidgets import PushButton

from modules.app_state import AppState


class ParamPage(QWidget):
    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setObjectName("param")

        title = QLabel("参数设定")
        title.setObjectName("pageTitle")

        self.fields = {}

        freq_group = self._group("频率参数")
        temp_group = self._group("温度参数")
        other_group = self._group("压力/时间参数")

        self._add_field(freq_group, "atomizer_freq", "雾化器频率", 0, 100)
        self._add_field(freq_group, "blower_freq", "鼓风机频率", 0, 100)
        self._add_field(freq_group, "induced_fan_freq", "引风机频率", 0, 100)
        self._add_field(other_group, "atomizer_vibration_limit", "雾化器震频上限", 0, 500)
        self._add_field(temp_group, "force_spray_temp", "强制喷水温度", 0, 200)
        self._add_field(temp_group, "feed_pump_open_temp", "加料泵开启温度", 0, 200)
        self._add_field(temp_group, "outlet_temp_set", "出风温度设定", 0, 200)
        self._add_field(temp_group, "emergency_fan_temp", "应急风机开启温度", 0, 200)
        self._add_field(other_group, "feed_pressure_high", "料液压力上限", 0, 50)
        self._add_field(temp_group, "atomizer_oil_temp", "雾化器油温", 0, 200)
        self._add_field(other_group, "start_stop_spray_time_min", "开关机喷水时间(min)", 0, 120)
        self._add_field(temp_group, "fan_stop_temp", "风机关闭温度", 0, 200)
        self._add_field(temp_group, "feed_pump_stop_temp", "加料泵关闭温度", 0, 200)

        save_btn = PushButton("保存参数")
        save_btn.clicked.connect(self._save)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(freq_group)
        layout.addWidget(temp_group)
        layout.addWidget(other_group)
        layout.addWidget(save_btn)
        layout.addStretch(1)

    def _group(self, title: str) -> QGroupBox:
        box = QGroupBox(title)
        box.setLayout(QFormLayout())
        return box

    def _add_field(self, group: QGroupBox, key: str, label: str, min_v: float, max_v: float) -> None:
        box = QDoubleSpinBox()
        box.setRange(min_v, max_v)
        box.setDecimals(2)
        box.setValue(getattr(self.state.params, key))
        self.fields[key] = box
        group.layout().addRow(label, box)

    def _save(self) -> None:
        for key, box in self.fields.items():
            setattr(self.state.params, key, box.value())

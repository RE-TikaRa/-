from PyQt6.QtWidgets import QCheckBox, QDoubleSpinBox, QFormLayout, QLabel, QVBoxLayout, QWidget, QGroupBox
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
        feed_group = self._group("加料泵参数")
        temp_group = self._group("温度参数")
        pressure_group = self._group("压力/时间/浓度")
        alarm_group = self._group("报警阈值")
        heater_group = self._group("电加热启用")

        self._add_field(freq_group, "atomizer_freq", "雾化器频率", 0, 100)
        self._add_field(freq_group, "blower_freq", "鼓风机频率", 0, 100)
        self._add_field(freq_group, "induced_fan_freq", "引风机频率", 0, 100)

        self._add_field(feed_group, "feed_freq", "加料频率", 0, 100)
        self._add_field(feed_group, "feed_manual_freq", "手动频率", 0, 100)
        self._add_field(feed_group, "feed_auto_min_freq", "自动下限", 0, 100)
        self._add_field(feed_group, "feed_auto_max_freq", "自动上限", 0, 100)
        self._add_field(feed_group, "feed_interval_min", "喷灰/卸料间隔(min)", 0, 120)

        self._add_field(temp_group, "force_spray_temp", "强制喷水温度", 0, 200)
        self._add_field(temp_group, "feed_pump_open_inlet_temp", "加料泵开启进风温度", 0, 200)
        self._add_field(temp_group, "feed_pump_open_outlet_temp", "加料泵开启出风温度", 0, 200)
        self._add_field(temp_group, "feed_pump_stop_temp", "加料泵关闭温度", 0, 200)
        self._add_field(temp_group, "outlet_temp_set", "出风温度设定", 0, 200)
        self._add_field(temp_group, "emergency_fan_temp", "应急风机开启温度", 0, 200)
        self._add_field(temp_group, "emergency_fan_auto_start_temp", "应急风机自动开启温度", 0, 200)
        self._add_field(temp_group, "fan_stop_temp", "风机关闭温度", 0, 200)
        self._add_field(temp_group, "atomizer_oil_temp", "雾化器油温", 0, 200)

        self._add_field(pressure_group, "feed_pressure_high", "料液压力上限", 0, 50)
        self._add_field(pressure_group, "dust_concentration_limit", "粉尘浓度上限", 0, 100)
        self._add_field(pressure_group, "atomizer_vibration_limit", "雾化器震频上限", 0, 500)
        self._add_field(pressure_group, "clean_ash_time_sec", "清灰工作时间(s)", 0, 60)
        self._add_field(pressure_group, "start_stop_spray_time_min", "开关机喷水时间(min)", 0, 120)
        self._add_field(pressure_group, "material_weight_low", "料罐重量下限", 0, 1000)
        self._add_field(pressure_group, "mixer_remind_weight", "搅拌电机提醒料罐重量", 0, 1000)

        self._add_field(alarm_group, "blower_fault_freq_low", "鼓风机故障频率下限", 0, 100)
        self._add_field(alarm_group, "blower_fault_freq_high", "鼓风机故障频率上限", 0, 100)
        self._add_field(alarm_group, "induced_fan_fault_freq_low", "引风机故障频率下限", 0, 100)
        self._add_field(alarm_group, "induced_fan_fault_freq_high", "引风机故障频率上限", 0, 100)
        self._add_field(alarm_group, "inlet_temp_low", "进风温度下限", 0, 200)
        self._add_field(alarm_group, "inlet_temp_high", "进风温度上限", 0, 200)
        self._add_field(alarm_group, "outlet_temp_low", "出风温度下限", 0, 200)
        self._add_field(alarm_group, "outlet_temp_high", "出风温度上限", 0, 200)
        self._add_field(alarm_group, "atomizer_fault_freq", "雾化器故障频率", 0, 100)
        self._add_field(alarm_group, "atomizer_oil_pressure_high", "雾化器油压上限", 0, 50)
        self._add_field(alarm_group, "atomizer_work_time_hours", "雾化器工作时间(h)", 0, 999)

        self._add_bool(heater_group, "heater_enable_1", "1#电加热启用")
        self._add_bool(heater_group, "heater_enable_2", "2#电加热启用")
        self._add_bool(heater_group, "heater_enable_3", "3#电加热启用")
        self._add_bool(heater_group, "heater_enable_4", "4#电加热启用")
        self._add_bool(heater_group, "heater_enable_5", "5#电加热启用")
        self._add_bool(heater_group, "heater_enable_6", "6#电加热启用")
        self._add_bool(heater_group, "heater_enable_7", "7#电加热启用")
        self._add_bool(heater_group, "heater_enable_8", "8#电加热启用")
        self._add_bool(heater_group, "heater_enable_9", "9#电加热启用")
        self._add_bool(heater_group, "heater_enable_10", "10#电加热启用")

        save_btn = PushButton("保存参数")
        save_btn.clicked.connect(self._save)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(freq_group)
        layout.addWidget(feed_group)
        layout.addWidget(temp_group)
        layout.addWidget(pressure_group)
        layout.addWidget(alarm_group)
        layout.addWidget(heater_group)
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

    def _add_bool(self, group: QGroupBox, key: str, label: str) -> None:
        box = QCheckBox()
        box.setChecked(bool(getattr(self.state.params, key)))
        self.fields[key] = box
        group.layout().addRow(label, box)

    def _save(self) -> None:
        for key, box in self.fields.items():
            if isinstance(box, QCheckBox):
                setattr(self.state.params, key, box.isChecked())
            else:
                setattr(self.state.params, key, box.value())

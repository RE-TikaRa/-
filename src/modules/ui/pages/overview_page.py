from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QFont, QPainter, QPen
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget, QFrame, QGridLayout
from qfluentwidgets import PushButton, SwitchButton

from modules.app_state import AppState
from modules.data_store import DataStore
from modules.simulator import Simulator


DEVICE_LABELS = {
    "oil_pump": "油泵",
    "cool_fan": "冷风机",
    "atomizer": "雾化器",
    "blower": "鼓风机",
    "induced_fan": "引风机",
    "heater": "加热",
    "feed_pump": "加料泵",
    "feed_valve": "料泵阀门",
}


class SparklineWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._values: list[float] = []
        self.setMinimumHeight(80)

    def set_values(self, values: list[float]) -> None:
        self._values = values
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        if len(self._values) < 2:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(self.palette().color(self.foregroundRole()))
        painter.setPen(pen)

        w = self.width()
        h = self.height()
        values = self._values[-30:]
        v_min = min(values)
        v_max = max(values)
        span = max(1e-6, v_max - v_min)

        points = []
        for i, v in enumerate(values):
            x = i * (w / max(1, len(values) - 1))
            y = h - ((v - v_min) / span) * (h - 8) - 4
            points.append(QPointF(x, y))

        for i in range(1, len(points)):
            painter.drawLine(points[i - 1], points[i])


class OverviewPage(QWidget):
    def __init__(self, state: AppState, sim: Simulator, store: DataStore) -> None:
        super().__init__()
        self.state = state
        self.sim = sim
        self.store = store
        self.setObjectName("overview")

        title = QLabel("主界面")
        title.setObjectName("pageTitle")

        self.demo_switch = SwitchButton("演示模式")
        self.demo_switch.setChecked(self.state.demo_mode)
        self.demo_switch.checkedChanged.connect(self.sim.set_demo_mode)

        self.auto_start_btn = PushButton("一键开机")
        self.auto_stop_btn = PushButton("一键关机")
        self.auto_start_btn.clicked.connect(self.sim.auto_start)
        self.auto_stop_btn.clicked.connect(self.sim.auto_stop)

        control_row = QHBoxLayout()
        control_row.addWidget(self.demo_switch)
        control_row.addWidget(self.auto_start_btn)
        control_row.addWidget(self.auto_stop_btn)
        control_row.addStretch(1)

        self.card_inlet = self._make_card("进风温度", "0.0", "℃")
        self.card_outlet = self._make_card("出风温度", "0.0", "℃")
        self.card_delta = self._make_card("主塔压差", "0.00", "kPa")
        self.card_alarm = self._make_card("报警统计", "0", "条", footnote="未清除 / 总数")
        self.card_running = self._make_card("运行设备", "0", "台", footnote="当前在线")
        self.card_mode = self._make_card("模式状态", "联锁", "", footnote="演示开关")

        cards = QGridLayout()
        cards.setHorizontalSpacing(12)
        cards.setVerticalSpacing(12)
        cards.addWidget(self.card_inlet, 0, 0)
        cards.addWidget(self.card_outlet, 0, 1)
        cards.addWidget(self.card_delta, 0, 2)
        cards.addWidget(self.card_alarm, 1, 0)
        cards.addWidget(self.card_running, 1, 1)
        cards.addWidget(self.card_mode, 1, 2)

        self.trend_card = QFrame()
        self.trend_card.setProperty("class", "card")
        trend_title = QLabel("出风温度趋势")
        trend_title.setObjectName("sectionTitle")
        self.sparkline = SparklineWidget()
        trend_layout = QVBoxLayout(self.trend_card)
        trend_layout.addWidget(trend_title)
        trend_layout.addWidget(self.sparkline)

        self.device_panel = QFrame()
        self.device_panel.setProperty("class", "card")
        device_title = QLabel("设备状态")
        device_title.setObjectName("sectionTitle")
        self.device_grid = QGridLayout()
        self._device_dots = {}
        row = 0
        col = 0
        for key, label in DEVICE_LABELS.items():
            dot = QLabel(" ")
            dot.setFixedSize(10, 10)
            dot.setStyleSheet("border-radius: 5px; background: #94A3B8;")
            self._device_dots[key] = dot
            name = QLabel(label)
            box = QHBoxLayout()
            box.addWidget(dot)
            box.addWidget(name)
            wrapper = QWidget()
            wrapper.setLayout(box)
            self.device_grid.addWidget(wrapper, row, col)
            col += 1
            if col >= 4:
                col = 0
                row += 1

        panel_layout = QVBoxLayout(self.device_panel)
        panel_layout.addWidget(device_title)
        panel_layout.addLayout(self.device_grid)

        self.device_label = QLabel()
        self.device_label.setProperty("class", "muted")

        main_row = QHBoxLayout()
        main_row.addWidget(self.trend_card, 3)
        main_row.addWidget(self.device_panel, 2)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addLayout(control_row)
        layout.addLayout(cards)
        layout.addLayout(main_row)
        layout.addWidget(self.device_label)
        layout.addStretch(1)

        self.sim.updated.connect(self.refresh)
        self.refresh()

    def _make_card(self, title: str, value: str, unit: str, footnote: str | None = None) -> QFrame:
        card = QFrame()
        card.setProperty("class", "card")
        card.setFixedHeight(120)

        title_label = QLabel(title)
        title_label.setObjectName("kpiTitle")

        value_label = QLabel(value)
        value_label.setObjectName("kpiValue")
        value_label.setFont(QFont("Fira Code", 18, 600))
        card._value_label = value_label  # type: ignore[attr-defined]

        unit_label = QLabel(unit)
        unit_label.setObjectName("kpiUnit")
        unit_label.setProperty("class", "muted")

        value_row = QHBoxLayout()
        value_row.addWidget(value_label)
        value_row.addWidget(unit_label)
        value_row.addStretch(1)

        footnote_label = QLabel(footnote or "")
        footnote_label.setObjectName("kpiFoot")
        footnote_label.setProperty("class", "muted")
        card._footnote_label = footnote_label  # type: ignore[attr-defined]

        layout = QVBoxLayout(card)
        layout.addWidget(title_label)
        layout.addLayout(value_row)
        layout.addWidget(footnote_label)
        layout.addStretch(1)
        return card

    def refresh(self) -> None:
        s = self.state.sensors
        self.card_inlet._value_label.setText(f"{s.inlet_temp:.1f}")  # type: ignore[attr-defined]
        self.card_outlet._value_label.setText(f"{s.outlet_temp:.1f}")  # type: ignore[attr-defined]
        self.card_delta._value_label.setText(f"{s.pressure_delta:.2f}")  # type: ignore[attr-defined]

        alarms = self.store.list_alarms(200)
        uncleared = sum(1 for a in alarms if not a.cleared)
        self.card_alarm._value_label.setText(f"{uncleared}")  # type: ignore[attr-defined]
        self.card_alarm._footnote_label.setText(f"未清除 / 总数：{uncleared} / {len(alarms)}")  # type: ignore[attr-defined]

        running = [k for k, v in self.state.devices.items() if v.is_on]
        self.card_running._value_label.setText(str(len(running)))  # type: ignore[attr-defined]
        self.card_running._footnote_label.setText(f"当前在线 / 总数：{len(running)} / {len(self.state.devices)}")  # type: ignore[attr-defined]
        self.card_mode._value_label.setText("演示" if self.state.demo_mode else "联锁")  # type: ignore[attr-defined]

        self.sparkline.set_values(self.sim.get_sparkline())

        self.device_label.setText("运行设备: " + ("、".join(running) if running else "无"))

        for key, dot in self._device_dots.items():
            is_on = self.state.devices[key].is_on
            color = "#22C55E" if is_on else "#94A3B8"
            dot.setStyleSheet(f"border-radius: 5px; background: {color};")

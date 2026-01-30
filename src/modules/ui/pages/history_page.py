from pathlib import Path

from PyQt6.QtCore import QDateTime, QTimer
from PyQt6.QtWidgets import (
    QDateTimeEdit,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import PushButton, SwitchButton

from modules.app_state import AppState
from modules.data_store import DataStore


class HistoryPage(QWidget):
    def __init__(self, state: AppState, store: DataStore) -> None:
        super().__init__()
        self.state = state
        self.store = store
        self.setObjectName("history")

        title = QLabel("历史数据")
        title.setObjectName("pageTitle")

        self.refresh_btn = PushButton("刷新")
        self.export_btn = PushButton("导出")
        self.refresh_btn.clicked.connect(self.refresh)
        self.export_btn.clicked.connect(self.export_data)

        self.filter_switch = SwitchButton("启用时间筛选")
        self.filter_switch.setChecked(False)

        self.start_dt = QDateTime.currentDateTime().addSecs(-3600)
        self.end_dt = QDateTime.currentDateTime()

        self.start_picker = QDateTimeEdit()
        self.start_picker.setDateTime(self.start_dt)
        self.start_picker.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.start_picker.setCalendarPopup(False)
        self.start_picker.setMinimumWidth(180)
        self.end_picker = QDateTimeEdit()
        self.end_picker.setDateTime(self.end_dt)
        self.end_picker.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_picker.setCalendarPopup(False)
        self.end_picker.setMinimumWidth(180)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        filter_row.addWidget(self.filter_switch)
        filter_row.addWidget(QLabel("开始"))
        filter_row.addWidget(self.start_picker)
        filter_row.addWidget(QLabel("结束"))
        filter_row.addWidget(self.end_picker)
        filter_row.addStretch(1)
        filter_row.addWidget(self.export_btn)
        filter_row.addWidget(self.refresh_btn)

        self.range_hint = QLabel("范围：最近 200 条")
        self.range_hint.setProperty("class", "muted")

        filter_panel = QFrame()
        filter_panel.setProperty("class", "card")
        filter_layout = QVBoxLayout(filter_panel)
        filter_layout.setContentsMargins(12, 12, 12, 12)
        filter_title = QLabel("筛选条件")
        filter_title.setObjectName("sectionTitle")
        filter_layout.addWidget(filter_title)
        filter_layout.addLayout(filter_row)
        filter_layout.addWidget(self.range_hint)

        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels(
            [
                "时间",
                "进风温度",
                "出风温度",
                "压差",
                "粉尘浓度",
                "料液压力",
                "雾化器油压",
                "鼓风机频率",
                "引风机频率",
                "雾化器频率",
            ]
        )
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        table_panel = QFrame()
        table_panel.setProperty("class", "card")
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(8, 8, 8, 8)
        table_layout.addWidget(self.table)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(filter_panel)
        layout.addWidget(table_panel)

        self._timer = QTimer(self)
        self._timer.setInterval(3000)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()

        self._last_rows = []
        self.refresh()

    def export_data(self) -> None:
        path, selected = QFileDialog.getSaveFileName(
            self,
            "导出历史数据",
            "",
            "CSV (*.csv);;Excel (*.xlsx);;JSON (*.json)",
        )
        if not path:
            return
        file_path = Path(path)
        if file_path.suffix == "":
            if "Excel" in selected:
                file_path = file_path.with_suffix(".xlsx")
            elif "JSON" in selected:
                file_path = file_path.with_suffix(".json")
            else:
                file_path = file_path.with_suffix(".csv")
        self.store.export_history(self._last_rows, file_path)

    def refresh(self) -> None:
        if self.filter_switch.isChecked():
            start = self.start_picker.dateTime().toPyDateTime()
            end = self.end_picker.dateTime().toPyDateTime()
            rows = self.store.list_history_range(start, end, 200)
            self.range_hint.setText(
                f"范围：{start.strftime('%Y-%m-%d %H:%M')} ~ {end.strftime('%Y-%m-%d %H:%M')}"
            )
        else:
            rows = self.store.list_history(200)
            self.range_hint.setText("范围：最近 200 条")

        self._last_rows = list(rows)
        self.table.setRowCount(len(self._last_rows))
        for i, row in enumerate(self._last_rows):
            self.table.setItem(i, 0, QTableWidgetItem(row.ts.strftime("%Y-%m-%d %H:%M:%S")))
            self.table.setItem(i, 1, QTableWidgetItem(f"{row.inlet_temp:.1f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{row.outlet_temp:.1f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{row.pressure_delta:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{row.dust_concentration:.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{row.feed_pressure:.2f}"))
            self.table.setItem(i, 6, QTableWidgetItem(f"{row.atomizer_oil_pressure:.2f}"))
            self.table.setItem(i, 7, QTableWidgetItem(f"{row.blower_freq:.1f}"))
            self.table.setItem(i, 8, QTableWidgetItem(f"{row.induced_fan_freq:.1f}"))
            self.table.setItem(i, 9, QTableWidgetItem(f"{row.atomizer_freq:.1f}"))

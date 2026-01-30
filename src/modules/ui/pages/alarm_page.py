from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import PushButton

from modules.app_state import AppState
from modules.data_store import DataStore
from modules.simulator import Simulator


class AlarmPage(QWidget):
    def __init__(self, state: AppState, store: DataStore, sim: Simulator) -> None:
        super().__init__()
        self.state = state
        self.store = store
        self.sim = sim
        self.setObjectName("alarm")

        title = QLabel("报警查看")
        title.setObjectName("pageTitle")

        self.refresh_btn = PushButton("刷新")
        self.export_btn = PushButton("导出")
        self.clear_btn = PushButton("报警消音")
        self.refresh_btn.clicked.connect(self.refresh)
        self.export_btn.clicked.connect(self.export_data)
        self.clear_btn.clicked.connect(self.clear_alarms)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["时间", "报警信息", "已消音"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        button_row = QHBoxLayout()
        button_row.addWidget(self.export_btn)
        button_row.addWidget(self.refresh_btn)
        button_row.addWidget(self.clear_btn)
        button_row.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addLayout(button_row)
        layout.addWidget(self.table)

        self._timer = QTimer(self)
        self._timer.setInterval(2000)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()

        self.sim.alarm_added.connect(lambda _: self.refresh())
        self._last_rows = []
        self.refresh()

    def export_data(self) -> None:
        path, selected = QFileDialog.getSaveFileName(
            self,
            "导出报警记录",
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
        self.store.export_alarms(self._last_rows, file_path)

    def clear_alarms(self) -> None:
        self.store.clear_alarms()
        self.refresh()

    def refresh(self) -> None:
        rows = self.store.list_alarms(200)
        self._last_rows = list(rows)
        self.table.setRowCount(len(self._last_rows))
        for i, row in enumerate(self._last_rows):
            self.table.setItem(i, 0, QTableWidgetItem(row.ts.strftime("%Y-%m-%d %H:%M:%S")))
            self.table.setItem(i, 1, QTableWidgetItem(row.message))
            self.table.setItem(i, 2, QTableWidgetItem("是" if row.cleared else "否"))

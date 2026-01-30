from __future__ import annotations

import csv
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


@dataclass
class AlarmRecord:
    ts: datetime
    message: str
    cleared: bool


@dataclass
class HistoryRecord:
    ts: datetime
    inlet_temp: float
    outlet_temp: float
    pressure_delta: float


class DataStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        self._init_schema()

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _init_schema(self) -> None:
        assert self._conn is not None
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS alarms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                message TEXT NOT NULL,
                cleared INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                inlet_temp REAL NOT NULL,
                outlet_temp REAL NOT NULL,
                pressure_delta REAL NOT NULL
            );
            """
        )
        self._conn.commit()

    def add_alarm(self, record: AlarmRecord) -> None:
        assert self._conn is not None
        self._conn.execute(
            "INSERT INTO alarms (ts, message, cleared) VALUES (?, ?, ?)",
            (record.ts.isoformat(), record.message, 1 if record.cleared else 0),
        )
        self._conn.commit()

    def list_alarms(self, limit: int = 200) -> List[AlarmRecord]:
        assert self._conn is not None
        rows = self._conn.execute(
            "SELECT ts, message, cleared FROM alarms ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            AlarmRecord(
                ts=datetime.fromisoformat(ts),
                message=message,
                cleared=bool(cleared),
            )
            for ts, message, cleared in rows
        ]

    def clear_alarms(self) -> None:
        assert self._conn is not None
        self._conn.execute("UPDATE alarms SET cleared = 1")
        self._conn.commit()

    def add_history(self, record: HistoryRecord) -> None:
        assert self._conn is not None
        self._conn.execute(
            "INSERT INTO history (ts, inlet_temp, outlet_temp, pressure_delta) VALUES (?, ?, ?, ?)",
            (
                record.ts.isoformat(),
                record.inlet_temp,
                record.outlet_temp,
                record.pressure_delta,
            ),
        )
        self._conn.commit()

    def list_history(self, limit: int = 500) -> List[HistoryRecord]:
        assert self._conn is not None
        rows = self._conn.execute(
            "SELECT ts, inlet_temp, outlet_temp, pressure_delta FROM history ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            HistoryRecord(
                ts=datetime.fromisoformat(ts),
                inlet_temp=inlet,
                outlet_temp=outlet,
                pressure_delta=delta,
            )
            for ts, inlet, outlet, delta in rows
        ]

    def list_history_range(
        self, start: datetime, end: datetime, limit: int = 500
    ) -> List[HistoryRecord]:
        assert self._conn is not None
        rows = self._conn.execute(
            """
            SELECT ts, inlet_temp, outlet_temp, pressure_delta
            FROM history
            WHERE ts BETWEEN ? AND ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (start.isoformat(), end.isoformat(), limit),
        ).fetchall()
        return [
            HistoryRecord(
                ts=datetime.fromisoformat(ts),
                inlet_temp=inlet,
                outlet_temp=outlet,
                pressure_delta=delta,
            )
            for ts, inlet, outlet, delta in rows
        ]

    def export_history(self, rows: Iterable[HistoryRecord], path: Path) -> None:
        suffix = path.suffix.lower()
        if suffix == ".json":
            payload = [
                {
                    "时间": row.ts.isoformat(sep=" ", timespec="seconds"),
                    "进风温度": row.inlet_temp,
                    "出风温度": row.outlet_temp,
                    "压差": row.pressure_delta,
                }
                for row in rows
            ]
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            return

        if suffix == ".xlsx":
            from openpyxl import Workbook

            wb = Workbook()
            ws = wb.active
            ws.title = "历史数据"
            ws.append(["时间", "进风温度", "出风温度", "压差"])
            for row in rows:
                ws.append(
                    [
                        row.ts.strftime("%Y-%m-%d %H:%M:%S"),
                        row.inlet_temp,
                        row.outlet_temp,
                        row.pressure_delta,
                    ]
                )
            wb.save(path)
            return

        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["时间", "进风温度", "出风温度", "压差"])
            for row in rows:
                writer.writerow(
                    [
                        row.ts.strftime("%Y-%m-%d %H:%M:%S"),
                        f"{row.inlet_temp:.2f}",
                        f"{row.outlet_temp:.2f}",
                        f"{row.pressure_delta:.3f}",
                    ]
                )

    def export_alarms(self, rows: Iterable[AlarmRecord], path: Path) -> None:
        suffix = path.suffix.lower()
        if suffix == ".json":
            payload = [
                {
                    "时间": row.ts.isoformat(sep=" ", timespec="seconds"),
                    "报警信息": row.message,
                    "已消音": row.cleared,
                }
                for row in rows
            ]
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            return

        if suffix == ".xlsx":
            from openpyxl import Workbook

            wb = Workbook()
            ws = wb.active
            ws.title = "报警记录"
            ws.append(["时间", "报警信息", "已消音"])
            for row in rows:
                ws.append(
                    [
                        row.ts.strftime("%Y-%m-%d %H:%M:%S"),
                        row.message,
                        "是" if row.cleared else "否",
                    ]
                )
            wb.save(path)
            return

        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["时间", "报警信息", "已消音"])
            for row in rows:
                writer.writerow(
                    [
                        row.ts.strftime("%Y-%m-%d %H:%M:%S"),
                        row.message,
                        "是" if row.cleared else "否",
                    ]
                )

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
    dust_concentration: float
    feed_pressure: float
    atomizer_oil_pressure: float
    blower_freq: float
    induced_fan_freq: float
    atomizer_freq: float


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
                pressure_delta REAL NOT NULL,
                dust_concentration REAL NOT NULL DEFAULT 0,
                feed_pressure REAL NOT NULL DEFAULT 0,
                atomizer_oil_pressure REAL NOT NULL DEFAULT 0,
                blower_freq REAL NOT NULL DEFAULT 0,
                induced_fan_freq REAL NOT NULL DEFAULT 0,
                atomizer_freq REAL NOT NULL DEFAULT 0
            );
            """
        )
        self._ensure_history_columns()
        self._conn.commit()

    def _ensure_history_columns(self) -> None:
        assert self._conn is not None
        existing = {row[1] for row in self._conn.execute("PRAGMA table_info(history)").fetchall()}
        columns = {
            "dust_concentration": "REAL NOT NULL DEFAULT 0",
            "feed_pressure": "REAL NOT NULL DEFAULT 0",
            "atomizer_oil_pressure": "REAL NOT NULL DEFAULT 0",
            "blower_freq": "REAL NOT NULL DEFAULT 0",
            "induced_fan_freq": "REAL NOT NULL DEFAULT 0",
            "atomizer_freq": "REAL NOT NULL DEFAULT 0",
        }
        for name, ddl in columns.items():
            if name not in existing:
                self._conn.execute(f"ALTER TABLE history ADD COLUMN {name} {ddl}")

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
            """
            INSERT INTO history (
                ts,
                inlet_temp,
                outlet_temp,
                pressure_delta,
                dust_concentration,
                feed_pressure,
                atomizer_oil_pressure,
                blower_freq,
                induced_fan_freq,
                atomizer_freq
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.ts.isoformat(),
                record.inlet_temp,
                record.outlet_temp,
                record.pressure_delta,
                record.dust_concentration,
                record.feed_pressure,
                record.atomizer_oil_pressure,
                record.blower_freq,
                record.induced_fan_freq,
                record.atomizer_freq,
            ),
        )
        self._conn.commit()

    def list_history(self, limit: int = 500) -> List[HistoryRecord]:
        assert self._conn is not None
        rows = self._conn.execute(
            """
            SELECT ts, inlet_temp, outlet_temp, pressure_delta,
                   dust_concentration, feed_pressure, atomizer_oil_pressure,
                   blower_freq, induced_fan_freq, atomizer_freq
            FROM history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            HistoryRecord(
                ts=datetime.fromisoformat(ts),
                inlet_temp=inlet,
                outlet_temp=outlet,
                pressure_delta=delta,
                dust_concentration=dust,
                feed_pressure=feed,
                atomizer_oil_pressure=oil_p,
                blower_freq=blower,
                induced_fan_freq=induced,
                atomizer_freq=atomizer,
            )
            for ts, inlet, outlet, delta, dust, feed, oil_p, blower, induced, atomizer in rows
        ]

    def list_history_range(
        self, start: datetime, end: datetime, limit: int = 500
    ) -> List[HistoryRecord]:
        assert self._conn is not None
        rows = self._conn.execute(
            """
            SELECT ts, inlet_temp, outlet_temp, pressure_delta,
                   dust_concentration, feed_pressure, atomizer_oil_pressure,
                   blower_freq, induced_fan_freq, atomizer_freq
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
                dust_concentration=dust,
                feed_pressure=feed,
                atomizer_oil_pressure=oil_p,
                blower_freq=blower,
                induced_fan_freq=induced,
                atomizer_freq=atomizer,
            )
            for ts, inlet, outlet, delta, dust, feed, oil_p, blower, induced, atomizer in rows
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
                    "粉尘浓度": row.dust_concentration,
                    "料液压力": row.feed_pressure,
                    "雾化器油压": row.atomizer_oil_pressure,
                    "鼓风机频率": row.blower_freq,
                    "引风机频率": row.induced_fan_freq,
                    "雾化器频率": row.atomizer_freq,
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
            ws.append(["时间", "进风温度", "出风温度", "压差", "粉尘浓度", "料液压力", "雾化器油压", "鼓风机频率", "引风机频率", "雾化器频率"])
            for row in rows:
                ws.append(
                    [
                        row.ts.strftime("%Y-%m-%d %H:%M:%S"),
                        row.inlet_temp,
                        row.outlet_temp,
                        row.pressure_delta,
                        row.dust_concentration,
                        row.feed_pressure,
                        row.atomizer_oil_pressure,
                        row.blower_freq,
                        row.induced_fan_freq,
                        row.atomizer_freq,
                    ]
                )
            wb.save(path)
            return

        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["时间", "进风温度", "出风温度", "压差", "粉尘浓度", "料液压力", "雾化器油压", "鼓风机频率", "引风机频率", "雾化器频率"])
            for row in rows:
                writer.writerow(
                    [
                        row.ts.strftime("%Y-%m-%d %H:%M:%S"),
                        f"{row.inlet_temp:.2f}",
                        f"{row.outlet_temp:.2f}",
                        f"{row.pressure_delta:.3f}",
                        f"{row.dust_concentration:.3f}",
                        f"{row.feed_pressure:.3f}",
                        f"{row.atomizer_oil_pressure:.3f}",
                        f"{row.blower_freq:.2f}",
                        f"{row.induced_fan_freq:.2f}",
                        f"{row.atomizer_freq:.2f}",
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

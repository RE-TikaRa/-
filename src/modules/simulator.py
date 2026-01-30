from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta
from typing import Callable, Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from modules.app_state import AppState, RunState
from modules.data_store import AlarmRecord, DataStore, HistoryRecord
from modules.interlock import Interlock


class Simulator(QObject):
    updated = pyqtSignal()
    alarm_added = pyqtSignal(str)

    def __init__(self, state: AppState, store: DataStore) -> None:
        super().__init__()
        self.state = state
        self.store = store
        self.interlock = Interlock(state)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self._last_history_at: Optional[datetime] = None
        self._auto_step = 0
        self._auto_start_time: Optional[datetime] = None
        self._auto_mode: Optional[str] = None
        self._last_alarm_at: Optional[datetime] = None
        self._sparkline = deque(maxlen=60)

    def start(self) -> None:
        if not self._timer.isActive():
            self._timer.start()

    def stop(self) -> None:
        if self._timer.isActive():
            self._timer.stop()

    def set_demo_mode(self, enabled: bool) -> None:
        self.state.demo_mode = enabled

    def get_sparkline(self) -> list[float]:
        return list(self._sparkline)

    def auto_start(self) -> None:
        self.state.auto_running = True
        self._auto_mode = "start"
        self._auto_step = 0
        self._auto_start_time = datetime.now()

    def auto_stop(self) -> None:
        self.state.auto_running = True
        self._auto_mode = "stop"
        self._auto_step = 0
        self._auto_start_time = datetime.now()

    def toggle_device(self, key: str, on: bool) -> str:
        device = self.state.devices[key]
        if on:
            check = self.interlock.can_start(key)
            if not check.ok:
                device.lock_reason = check.reason
                return check.reason
            device.is_on = True
            device.run_state = RunState.RUNNING
            device.lock_reason = ""
        else:
            device.is_on = False
            device.run_state = RunState.STOPPED
            device.lock_reason = ""
        return ""

    def _tick(self) -> None:
        self._update_sensors()
        self._update_auto_sequence()
        self._write_history_if_needed()
        self._check_alarms()
        self.updated.emit()

    def _update_sensors(self) -> None:
        s = self.state.sensors
        d = self.state.devices

        if d["heater"].is_on:
            s.inlet_temp += 0.4
            s.outlet_temp += 0.3
        else:
            s.inlet_temp = max(25.0, s.inlet_temp - 0.2)
            s.outlet_temp = max(25.0, s.outlet_temp - 0.2)

        if d["blower"].is_on and d["induced_fan"].is_on:
            s.pressure_delta = max(-0.6, min(-0.2, s.pressure_delta - 0.02))
        else:
            s.pressure_delta = -0.1

        self._sparkline.append(s.outlet_temp)

    def _update_auto_sequence(self) -> None:
        if not self.state.auto_running:
            return

        if self._auto_mode == "start":
            steps = [
                ("dust_cleaner", True),
                ("air_hammer", True),
                ("discharge_fan", True),
                ("oil_pump", True),
                ("cool_fan", True),
                ("atomizer", True),
                ("feed_valve", True),
                ("feed_pump", True),
                ("blower", True),
                ("induced_fan", True),
                ("heater", True),
            ]
        else:
            steps = [
                ("heater", False),
                ("feed_pump", False),
                ("feed_valve", False),
                ("atomizer", False),
                ("cool_fan", False),
                ("oil_pump", False),
                ("induced_fan", False),
                ("blower", False),
                ("discharge_fan", False),
                ("air_hammer", False),
                ("dust_cleaner", False),
            ]

        if self._auto_step < len(steps):
            key, on = steps[self._auto_step]
            reason = self.toggle_device(key, on)
            if not reason:
                self._auto_step += 1
            return

        self.state.auto_running = False
        self._auto_mode = None

    def _write_history_if_needed(self) -> None:
        now = datetime.now()
        if self._last_history_at is None:
            self._last_history_at = now
        if now - self._last_history_at >= timedelta(seconds=5):
            s = self.state.sensors
            self.store.add_history(
                HistoryRecord(
                    ts=now,
                    inlet_temp=s.inlet_temp,
                    outlet_temp=s.outlet_temp,
                    pressure_delta=s.pressure_delta,
                )
            )
            self._last_history_at = now

    def _check_alarms(self) -> None:
        s = self.state.sensors
        if s.outlet_temp > self.state.params.force_spray_temp:
            now = datetime.now()
            if self._last_alarm_at is None or now - self._last_alarm_at >= timedelta(seconds=10):
                msg = "出风温度高报警"
                self.store.add_alarm(AlarmRecord(ts=now, message=msg, cleared=False))
                self.alarm_added.emit(msg)
                self._last_alarm_at = now

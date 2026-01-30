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
        self._last_feed_interval_at: Optional[datetime] = None

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
        p = self.state.params
        now = datetime.now()

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

        s.blower_freq = p.blower_freq if d["blower"].is_on else 0.0
        s.induced_fan_freq = p.induced_fan_freq if d["induced_fan"].is_on else 0.0
        s.atomizer_freq = p.atomizer_freq if d["atomizer"].is_on else 0.0

        if d["feed_pump"].is_on:
            s.feed_pressure = min(p.feed_pressure_high + 2.0, s.feed_pressure + 0.4)
        else:
            s.feed_pressure = max(1.0, s.feed_pressure - 0.3)

        if d["atomizer"].is_on:
            s.atomizer_oil_pressure = min(p.atomizer_oil_pressure_high + 2.0, s.atomizer_oil_pressure + 0.3)
        else:
            s.atomizer_oil_pressure = max(3.0, s.atomizer_oil_pressure - 0.2)

        if d["dust_cleaner"].is_on or d["air_hammer"].is_on:
            factor = 3.0 / max(1.0, p.clean_ash_time_sec)
            s.dust_concentration = max(0.5, s.dust_concentration - 0.2 * factor)
        else:
            s.dust_concentration = min(p.dust_concentration_limit + 5.0, s.dust_concentration + 0.1)

        if self._last_feed_interval_at is None:
            self._last_feed_interval_at = now

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
                    dust_concentration=s.dust_concentration,
                    feed_pressure=s.feed_pressure,
                    atomizer_oil_pressure=s.atomizer_oil_pressure,
                    blower_freq=s.blower_freq,
                    induced_fan_freq=s.induced_fan_freq,
                    atomizer_freq=s.atomizer_freq,
                )
            )
            self._last_history_at = now

    def _check_alarms(self) -> None:
        s = self.state.sensors
        p = self.state.params
        d = self.state.devices
        now = datetime.now()
        if self._last_alarm_at is None:
            self._last_alarm_at = now - timedelta(seconds=30)

        alarms = []
        if s.outlet_temp > p.force_spray_temp:
            alarms.append("出风温度高报警")
        if s.inlet_temp < p.inlet_temp_low:
            alarms.append("进风温度低报警")
        if s.inlet_temp > p.inlet_temp_high:
            alarms.append("进风温度高报警")
        if s.outlet_temp < p.outlet_temp_low:
            alarms.append("出风温度低报警")
        if s.outlet_temp > p.outlet_temp_high:
            alarms.append("出风温度高报警")

        if s.dust_concentration > p.dust_concentration_limit:
            alarms.append("粉尘浓度高报警")
        if s.feed_pressure > p.feed_pressure_high:
            alarms.append("料液压力高报警")
        if s.atomizer_oil_pressure > p.atomizer_oil_pressure_high:
            alarms.append("雾化器油压高报警")
        if d["blower"].is_on and (
            s.blower_freq < p.blower_fault_freq_low or s.blower_freq > p.blower_fault_freq_high
        ):
            alarms.append("鼓风机故障频率报警")
        if d["induced_fan"].is_on and (
            s.induced_fan_freq < p.induced_fan_fault_freq_low
            or s.induced_fan_freq > p.induced_fan_fault_freq_high
        ):
            alarms.append("引风机故障频率报警")
        if d["atomizer"].is_on and s.atomizer_freq < p.atomizer_fault_freq:
            alarms.append("雾化器故障频率报警")
        if d["feed_pump"].is_on and self._last_feed_interval_at is not None:
            if now - self._last_feed_interval_at >= timedelta(minutes=p.feed_interval_min):
                alarms.append("喷灰/卸料间隔到")
                self._last_feed_interval_at = now

        if alarms and now - self._last_alarm_at >= timedelta(seconds=10):
            for msg in alarms:
                self.store.add_alarm(AlarmRecord(ts=now, message=msg, cleared=False))
                self.alarm_added.emit(msg)
            self._last_alarm_at = now

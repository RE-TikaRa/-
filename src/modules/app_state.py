from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class RunState(str, Enum):
    STOPPED = "stopped"
    WAITING = "waiting"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class DeviceState:
    name: str
    is_on: bool = False
    run_state: RunState = RunState.STOPPED
    lock_reason: str = ""


@dataclass
class Sensors:
    inlet_temp: float = 25.0
    outlet_temp: float = 25.0
    pressure_delta: float = -0.1
    dust_concentration: float = 5.0
    feed_pressure: float = 2.0
    atomizer_oil_pressure: float = 6.0
    blower_freq: float = 0.0
    induced_fan_freq: float = 0.0
    atomizer_freq: float = 0.0


@dataclass
class Params:
    atomizer_freq: float = 40.0
    blower_freq: float = 40.0
    induced_fan_freq: float = 40.0
    atomizer_vibration_limit: float = 250.0
    force_spray_temp: float = 120.0
    feed_pump_open_temp: float = 80.0
    feed_pump_open_inlet_temp: float = 80.0
    feed_pump_open_outlet_temp: float = 80.0
    outlet_temp_set: float = 90.0
    emergency_fan_temp: float = 120.0
    emergency_fan_auto_start_temp: float = 120.0
    feed_pressure_high: float = 12.3
    dust_concentration_limit: float = 12.3
    atomizer_oil_temp: float = 60.0
    atomizer_oil_pressure_high: float = 12.3
    atomizer_fault_freq: float = 12.3
    atomizer_work_time_hours: float = 12.3
    start_stop_spray_time_min: float = 40.0
    clean_ash_time_sec: float = 3.0
    fan_stop_temp: float = 50.0
    feed_pump_stop_temp: float = 60.0
    material_weight_low: float = 12.0
    mixer_remind_weight: float = 12.0
    feed_freq: float = 12.3
    feed_manual_freq: float = 12.3
    feed_auto_min_freq: float = 12.3
    feed_auto_max_freq: float = 12.3
    feed_interval_min: float = 3.0
    blower_fault_freq_low: float = 12.3
    blower_fault_freq_high: float = 12.3
    induced_fan_fault_freq_low: float = 12.3
    induced_fan_fault_freq_high: float = 12.3
    inlet_temp_low: float = 12.3
    inlet_temp_high: float = 12.3
    outlet_temp_low: float = 12.3
    outlet_temp_high: float = 12.3
    heater_enable_1: bool = True
    heater_enable_2: bool = True
    heater_enable_3: bool = True
    heater_enable_4: bool = True
    heater_enable_5: bool = True
    heater_enable_6: bool = True
    heater_enable_7: bool = True
    heater_enable_8: bool = True
    heater_enable_9: bool = True
    heater_enable_10: bool = True


@dataclass
class AppState:
    demo_mode: bool = False
    auto_running: bool = False
    devices: Dict[str, DeviceState] = field(default_factory=dict)
    sensors: Sensors = field(default_factory=Sensors)
    params: Params = field(default_factory=Params)

    def init_defaults(self) -> None:
        for key in [
            "oil_pump",
            "cool_fan",
            "atomizer",
            "blower",
            "induced_fan",
            "heater",
            "feed_valve",
            "feed_pump",
            "dust_cleaner",
            "air_hammer",
            "discharge_fan",
        ]:
            self.devices[key] = DeviceState(name=key)

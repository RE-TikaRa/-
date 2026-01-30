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


@dataclass
class Params:
    atomizer_freq: float = 40.0
    blower_freq: float = 40.0
    induced_fan_freq: float = 40.0
    atomizer_vibration_limit: float = 250.0
    force_spray_temp: float = 120.0
    feed_pump_open_temp: float = 80.0
    outlet_temp_set: float = 90.0
    emergency_fan_temp: float = 120.0
    feed_pressure_high: float = 12.3
    atomizer_oil_temp: float = 60.0
    start_stop_spray_time_min: float = 40.0
    fan_stop_temp: float = 50.0
    feed_pump_stop_temp: float = 60.0


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

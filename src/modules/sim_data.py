from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Alarm:
    ts: datetime
    message: str
    cleared: bool = False


@dataclass
class HistoryPoint:
    ts: datetime
    inlet_temp: float
    outlet_temp: float
    pressure_delta: float


@dataclass
class SimData:
    alarms: List[Alarm]
    history: List[HistoryPoint]

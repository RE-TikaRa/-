from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from modules.app_state import AppState


@dataclass
class CheckResult:
    ok: bool
    reason: str = ""


class Interlock:
    def __init__(self, state: AppState) -> None:
        self.state = state

    def can_start(self, device: str) -> CheckResult:
        s = self.state
        d = s.devices

        if s.demo_mode:
            return CheckResult(True, "")

        if device == "oil_pump":
            if d["atomizer"].is_on:
                return CheckResult(False, "雾化器运行中，禁止关闭油泵")
            return CheckResult(True, "")

        if device == "cool_fan":
            return CheckResult(True, "")

        if device == "atomizer":
            if not d["oil_pump"].is_on:
                return CheckResult(False, "油泵未开启")
            if d["blower"].is_on or d["induced_fan"].is_on:
                return CheckResult(False, "鼓风机或引风机已开启")
            return CheckResult(True, "")

        if device == "blower":
            if not d["atomizer"].is_on:
                return CheckResult(False, "雾化器未开启")
            return CheckResult(True, "")

        if device == "induced_fan":
            if not d["blower"].is_on:
                return CheckResult(False, "鼓风机未开启")
            return CheckResult(True, "")

        if device == "heater":
            if not d["blower"].is_on or not d["induced_fan"].is_on:
                return CheckResult(False, "鼓风机/引风机未开启")
            if not (-0.6 <= s.sensors.pressure_delta <= -0.2):
                return CheckResult(False, "主塔压差不在范围内")
            if not any(
                (
                    s.params.heater_enable_1,
                    s.params.heater_enable_2,
                    s.params.heater_enable_3,
                    s.params.heater_enable_4,
                    s.params.heater_enable_5,
                    s.params.heater_enable_6,
                    s.params.heater_enable_7,
                    s.params.heater_enable_8,
                    s.params.heater_enable_9,
                    s.params.heater_enable_10,
                )
            ):
                return CheckResult(False, "电加热未启用")
            return CheckResult(True, "")

        if device == "feed_valve":
            return CheckResult(True, "")

        if device == "feed_pump":
            if not d["feed_valve"].is_on:
                return CheckResult(False, "料泵阀门未开启")
            if s.sensors.inlet_temp < s.params.feed_pump_open_inlet_temp:
                return CheckResult(False, "进风温度未达到开启条件")
            if s.sensors.outlet_temp < s.params.feed_pump_open_outlet_temp:
                return CheckResult(False, "出风温度未达到开启条件")
            return CheckResult(True, "")

        return CheckResult(True, "")

# Assembly Process Simulation and Optimization Validation Platform

A local demo project for portfolio presentation, reproducing typical workflows, interlock logic, alarm mechanisms, and data display of an assembly process system. The project does not connect to real equipment and is only for learning and presentation.

> Current version: V2.0
> Finalized date: January 30, 2026
> Author: TikaRa / ALp_Studio
> Original system name: Mechanical Assembly Process Simulation and Optimization System

## Project Overview
- Audience: course/project presentation for Mechanical Design, Manufacturing and Automation
- Goal: demonstrate process flow, interlocks, parameter settings, alarms, and history data via a visual UI and state machine
- Note: for demo only, not for on-site control

## Main Features (Demo)
- Home: system overview and status hints
- History: time-range query (simulated data), export to CSV / Excel / JSON
- Alarms: alarm list and mute logic (mute only, does not clear alarms), export to CSV / Excel / JSON
- Operation: device start/stop and status indicators
- Parameters: key process parameter configuration (including electric heater enable and alarm thresholds)
- One-click start/stop: auto demo following manual procedures

## Key Flow (Demo Logic)
Startup flow:
1. Dust cleaning / air hammer / rotary airlock fan
2. Oil pump / cooling fan
3. Atomizer
4. Feed pump valve / feed pump
5. Blower / induced draft fan
6. Heating
7. Water spray, switch to material spray after $t \\ge 40\\,\\text{min}$

Shutdown flow:
1. Water spray, keep $t \\ge 40\\,\\text{min}$
2. Stop heating
3. Feed pump standby/stop, close feed pump and valve
4. Stop atomizer (after countdown)
5. Stop oil pump / cooling fan
6. Stop induced draft fan / blower after $T_{in} < 50\\,^{\\circ}\\mathrm{C}$
7. Stop dust cleaning / air hammer / rotary airlock fan

## Technical Stack (V2.0)
- Language & framework: Python 3.13 + PyQt6 + QFluentWidgets
- Architecture: state machine (flow & interlock) + data simulation (history/alarms/parameters) + local persistence
- Storage: SQLite (history and alarms)
- Export dependency: openpyxl (Excel export)

## Directory Structure
```
.
├─ README.md
├─ docs/                # project docs and manuals
├─ img/                 # screenshots
├─ data/                # SQLite database
├─ src/                 # code
│  ├─ main.py           # entry
│  └─ modules/          # state/simulation/interlock/UI/data
└─ tools/               # helper scripts
```

## Usage
1. Install dependencies (UV)
   - `uv sync`
2. Run
   - `python src/main.py`
3. Use the UI for demo

## Parameters & History Fields (V2.0 Summary)
- New parameters: dust concentration limit, dust cleaning work time, tank weight lower limit / reminder weight, feed pump params, fan/atomizer fault thresholds, electric heater enable, etc.
- New history fields: dust concentration, feed liquid pressure, atomizer oil pressure, blower frequency, induced draft fan frequency, atomizer frequency.

## Screenshots
Home:
![Home](https://s2.loli.net/2026/01/30/lvdtc8iwGzM91JC.png)

History:
![History](https://s2.loli.net/2026/01/30/HY6arMGAk8uBzDf.png)

Alarms:
![Alarms](https://s2.loli.net/2026/01/30/8A7Bmobflp4XaqG.png)

Operation:
![Operation](https://s2.loli.net/2026/01/30/BlZ8kSsLOqz9FdC.png)

Parameters:
![Parameters](https://s2.loli.net/2026/01/30/BbDX8yNGT7grcwY.png)

## Sources
- Manuals and UI screenshots: `docs/manual/`
- PLC export and text reference: `docs/plc/`
- Specification: `docs/spec/`

## License
Apache-2.0. See `LICENSE`.

## Disclaimer
This project is for demo and learning only. It does not connect to real equipment and has no industrial on-site control capability.

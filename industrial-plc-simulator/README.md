# Industrial PLC Simulator

Visual PLC / Industrial Equipment Simulator for non-technical users.

## 1. Goal
Create a visual simulator of PLC/industrial equipment where users can:
- Load a default plant.
- Create their own industrial plant.
- Configure equipment, sensors, actuators, commands, alarms, and registers.
- Start/Stop a virtual PLC via Modbus TCP.
- Visualize simulated values in real-time.

## 2. Architecture
- **UI**: PySide6 (Desktop GUI)
- **Simulation Engine**: Python-based logic for sensors, actuators, and rules.
- **PLC Virtual**: PyModbus TCP Server.

## 3. Installation

```bash
# Create virtual environment
python -m venv .venv
# Activate virtual environment
.venv\Scripts\activate
# Install project and dependencies
pip install -e .
pip install -e ".[dev]"
```

## 4. How to Run

```bash
python -m app.main
```

## 5. Testing and Quality

```bash
# Run tests
pytest
# Run linter
pylint app
```

## 6. Features
- Hierarchical plant structure: Plant -> Area -> Line -> Equipment -> Tag.
- Modbus TCP server (Coils, Discrete Inputs, Holding Registers, Input Registers).
- Various simulation modes: Constant, Random, Random Walk, Counter, etc.
- JSON Import/Export.
- Tag map export for external tools.

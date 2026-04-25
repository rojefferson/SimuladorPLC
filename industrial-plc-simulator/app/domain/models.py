from dataclasses import dataclass, field
from typing import List, Optional, Any
from app.domain.enums import TagType, DataType, ModbusTable, SimulationMode

@dataclass
class ModbusConfig:
    table: ModbusTable
    address: int
    scale: float = 1.0

@dataclass
class SimulationSettings:
    mode: SimulationMode
    min: float = 0.0
    max: float = 100.0
    initial_value: Any = None
    alarm_low: Optional[float] = None
    alarm_high: Optional[float] = None

@dataclass
class Tag:
    name: str
    tag_type: TagType
    data_type: DataType
    unit: Optional[str] = None
    modbus: Optional[ModbusConfig] = None
    simulation: Optional[SimulationSettings] = None
    description: str = ""
    current_value: Any = None

@dataclass
class Equipment:
    name: str
    description: str = ""
    tags: List[Tag] = field(default_factory=list)

@dataclass
class Line:
    name: str
    equipments: List[Equipment] = field(default_factory=list)

@dataclass
class Area:
    name: str
    lines: List[Line] = field(default_factory=list)

@dataclass
class Plant:
    name: str
    areas: List[Area] = field(default_factory=list)

@dataclass
class ModbusServerConfig:
    host: str = "127.0.0.1"
    port: int = 5020
    unit_id: int = 1

@dataclass
class SimulationConfig:
    simulation_name: str
    version: str = "1.0"
    modbus_server: ModbusServerConfig = field(default_factory=ModbusServerConfig)
    plant: Plant = field(default_factory=lambda: Plant("New Plant"))

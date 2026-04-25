import json
import os
from enum import Enum
from dataclasses import asdict, is_dataclass
from typing import Any
from app.domain.models import SimulationConfig, ModbusServerConfig, Plant, Area, Line, Equipment, Tag, ModbusConfig, SimulationSettings
from app.domain.enums import TagType, DataType, ModbusTable, SimulationMode

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, Enum):
            return o.value
        return super().default(o)

def save_simulation(config: SimulationConfig, filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(asdict(config), f, cls=EnhancedJSONEncoder, indent=2, ensure_ascii=False)

def load_simulation(filepath: str) -> SimulationConfig:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Reconstruct objects from dict
    # This is a bit manual but robust for simple dataclasses
    
    mb_data = data.get("modbus_server", {})
    mb_server = ModbusServerConfig(
        host=mb_data.get("host", "127.0.0.1"),
        port=mb_data.get("port", 5020),
        unit_id=mb_data.get("unit_id", 1)
    )
    
    plant_data = data.get("plant", {})
    areas = []
    for area_d in plant_data.get("areas", []):
        lines = []
        for line_d in area_d.get("lines", []):
            equipments = []
            for equip_d in line_d.get("equipments", []):
                tags = []
                for tag_d in equip_d.get("tags", []):
                    mb_conf = None
                    if tag_d.get("modbus"):
                        mc = tag_d["modbus"]
                        mb_conf = ModbusConfig(
                            table=ModbusTable(mc["table"]),
                            address=mc["address"],
                            scale=mc.get("scale", 1.0)
                        )
                    
                    sim_conf = None
                    if tag_d.get("simulation"):
                        sc = tag_d["simulation"]
                        sim_conf = SimulationSettings(
                            mode=SimulationMode(sc["mode"]),
                            min=sc.get("min", 0.0),
                            max=sc.get("max", 100.0),
                            initial_value=sc.get("initial_value"),
                            alarm_low=sc.get("alarm_low"),
                            alarm_high=sc.get("alarm_high")
                        )
                    
                    tags.append(Tag(
                        name=tag_d["name"],
                        tag_type=TagType(tag_d["tag_type"]),
                        data_type=DataType(tag_d["data_type"]),
                        unit=tag_d.get("unit"),
                        modbus=mb_conf,
                        simulation=sim_conf,
                        description=tag_d.get("description", ""),
                        current_value=tag_d.get("current_value")
                    ))
                equipments.append(Equipment(
                    name=equip_d["name"],
                    description=equip_d.get("description", ""),
                    tags=tags
                ))
            lines.append(Line(
                name=line_d["name"],
                equipments=equipments
            ))
        areas.append(Area(
            name=area_d["name"],
            lines=lines
        ))
        
    plant = Plant(name=plant_data.get("name", "New Plant"), areas=areas)
    
    return SimulationConfig(
        simulation_name=data["simulation_name"],
        version=data.get("version", "1.0"),
        modbus_server=mb_server,
        plant=plant
    )

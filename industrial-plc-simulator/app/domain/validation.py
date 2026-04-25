from typing import List, Tuple
from app.domain.models import SimulationConfig, Tag

def validate_simulation_config(config: SimulationConfig) -> List[str]:
    errors = []
    
    if not config.simulation_name:
        errors.append("Simulation name is required.")
        
    if not config.plant.name:
        errors.append("Plant name is required.")
        
    # Check for duplicate modbus addresses
    addresses = {
        "coil": set(),
        "discrete_input": set(),
        "holding_register": set(),
        "input_register": set()
    }
    
    for area in config.plant.areas:
        for line in area.lines:
            for equipment in line.equipments:
                for tag in equipment.tags:
                    if tag.modbus:
                        table = tag.modbus.table.value
                        addr = tag.modbus.address
                        if addr in addresses[table]:
                            errors.append(f"Duplicate Modbus address {addr} in table {table} (Tag: {tag.name})")
                        addresses[table].add(addr)
                    
                    if tag.simulation:
                        if tag.simulation.min > tag.simulation.max:
                            errors.append(f"Tag {tag.name}: Min value cannot be greater than max value.")
                            
    return errors

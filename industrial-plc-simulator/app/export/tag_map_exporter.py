import json
from app.domain.models import SimulationConfig

def export_tag_map(config: SimulationConfig, filepath: str):
    tags_list = []
    
    for area in config.plant.areas:
        for line in area.lines:
            for equipment in line.equipments:
                for tag in equipment.tags:
                    tag_info = {
                        "equipment": equipment.name,
                        "tag": tag.name,
                        "tag_type": tag.tag_type.value,
                        "data_type": tag.data_type.value,
                        "unit": tag.unit,
                        "description": tag.description
                    }
                    
                    if tag.modbus:
                        tag_info["modbus_table"] = tag.modbus.table.value
                        tag_info["modbus_address"] = tag.modbus.address
                        tag_info["scale"] = tag.modbus.scale
                    
                    tags_list.append(tag_info)
                    
    output = {
        "plant": config.plant.name,
        "modbus_server": {
            "host": config.modbus_server.host,
            "port": config.modbus_server.port,
            "unit_id": config.modbus_server.unit_id
        },
        "tags": tags_list
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

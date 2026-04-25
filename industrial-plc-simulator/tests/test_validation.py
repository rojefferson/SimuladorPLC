from app.domain.models import SimulationConfig, Plant, Area, Line, Equipment, Tag, ModbusConfig
from app.domain.enums import TagType, DataType, ModbusTable
from app.domain.validation import validate_simulation_config

def test_duplicate_address_validation():
    mb1 = ModbusConfig(ModbusTable.COIL, 1)
    mb2 = ModbusConfig(ModbusTable.COIL, 1) # Duplicate
    
    tag1 = Tag("Tag1", TagType.DIGITAL_OUTPUT, DataType.BOOL, modbus=mb1)
    tag2 = Tag("Tag2", TagType.DIGITAL_OUTPUT, DataType.BOOL, modbus=mb2)
    
    equip = Equipment("Equip", tags=[tag1, tag2])
    line = Line("Line", equipments=[equip])
    area = Area("Area", lines=[line])
    plant = Plant("Plant", areas=[area])
    config = SimulationConfig("TestSim", plant=plant)
    
    errors = validate_simulation_config(config)
    assert any("Duplicate Modbus address 1" in e for e in errors)

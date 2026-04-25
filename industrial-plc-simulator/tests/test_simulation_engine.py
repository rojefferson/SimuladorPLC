from app.domain.models import SimulationConfig, Plant, Area, Line, Equipment, Tag, SimulationSettings
from app.domain.enums import TagType, DataType, SimulationMode
from app.simulation.engine import SimulationEngine
import time

def test_engine_updates_values():
    tag = Tag(
        "RandomTag", 
        TagType.ANALOG_INPUT, 
        DataType.FLOAT, 
        simulation=SimulationSettings(mode=SimulationMode.RANDOM, min=10, max=20)
    )
    equip = Equipment("Equip", tags=[tag])
    line = Line("Line", equipments=[equip])
    area = Area("Area", lines=[line])
    plant = Plant("Plant", areas=[area])
    config = SimulationConfig("TestSim", plant=plant)
    
    engine = SimulationEngine(config)
    engine._update_values()
    
    val = tag.current_value
    assert val is not None
    assert 10 <= val <= 20

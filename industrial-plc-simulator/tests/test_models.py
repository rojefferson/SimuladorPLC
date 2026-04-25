from app.domain.models import Plant, Area, Line, Equipment, Tag
from app.domain.enums import TagType, DataType

def test_plant_structure():
    tag = Tag("TestTag", TagType.ANALOG_INPUT, DataType.FLOAT)
    equip = Equipment("TestEquip", tags=[tag])
    line = Line("TestLine", equipments=[equip])
    area = Area("TestArea", lines=[line])
    plant = Plant("TestPlant", areas=[area])
    
    assert plant.name == "TestPlant"
    assert plant.areas[0].name == "TestArea"
    assert plant.areas[0].lines[0].equipments[0].tags[0].name == "TestTag"

import pytest
from app.domain.models import Tag, ModbusConfig, ModbusServerConfig
from app.domain.enums import TagType, DataType, ModbusTable
from app.ui.node_red_tooltip import build_node_red_tooltip, get_node_red_address, get_conventional_address

def test_tooltip_holding_register():
    tag = Tag(
        name="TemperaturaMotor",
        tag_type=TagType.ANALOG_INPUT,
        data_type=DataType.FLOAT,
        modbus=ModbusConfig(table=ModbusTable.HOLDING_REGISTER, address=20, scale=10.0),
        unit="Celsius"
    )
    server = ModbusServerConfig(host="127.0.0.1", port=5020, unit_id=1)
    
    tooltip = build_node_red_tooltip(tag, server)
    
    assert "FC 3: Read Holding Registers" in tooltip
    assert "Address Node-RED: 20" in tooltip
    assert "Endereço configurado: 40020" in tooltip
    assert "raw = msg.payload[0]" in tooltip
    assert "value = raw / 10.0" in tooltip
    assert "Unidade: Celsius" in tooltip

def test_tooltip_coil_write():
    tag = Tag(
        name="LigarMotor",
        tag_type=TagType.COMMAND,
        data_type=DataType.BOOL,
        modbus=ModbusConfig(table=ModbusTable.COIL, address=100)
    )
    server = ModbusServerConfig(host="127.0.0.1", port=5020, unit_id=1)
    
    tooltip = build_node_red_tooltip(tag, server)
    
    assert "Node-RED Modbus-Write" in tooltip
    assert "FC 1: Read Coils" in tooltip
    assert "FC escrita: FC 5: Force Single Coil" in tooltip
    assert "Address Node-RED: 100" in tooltip
    assert "Boolean(msg.payload[0])" in tooltip

def test_address_mapping():
    # Our project uses 1-based address configuration that maps directly to protocol
    assert get_node_red_address(20) == 20
    assert get_conventional_address(ModbusTable.HOLDING_REGISTER, 20) == "40020"
    assert get_conventional_address(ModbusTable.COIL, 1) == "1"

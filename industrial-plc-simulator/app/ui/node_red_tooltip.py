from app.domain.models import Tag, ModbusConfig, ModbusServerConfig
from app.domain.enums import TagType, ModbusTable, DataType

def get_read_fc_for_table(table: ModbusTable) -> str:
    mapping = {
        ModbusTable.COIL: "FC 1: Read Coils",
        ModbusTable.DISCRETE_INPUT: "FC 2: Read Discrete Inputs",
        ModbusTable.HOLDING_REGISTER: "FC 3: Read Holding Registers",
        ModbusTable.INPUT_REGISTER: "FC 4: Read Input Registers"
    }
    return mapping.get(table, "FC 3: Read Holding Registers")

def get_write_fc_for_table(table: ModbusTable) -> str:
    mapping = {
        ModbusTable.COIL: "FC 5: Force Single Coil",
        ModbusTable.HOLDING_REGISTER: "FC 6: Preset Single Register"
    }
    return mapping.get(table, "")

def get_node_red_address(configured_address: int) -> int:
    # Our project uses 1-based configured addresses for the first register.
    # Protocol-wise, this is address '1'.
    # Node-RED usually expects the protocol address directly.
    return configured_address

def get_conventional_address(table: ModbusTable, address: int) -> str:
    base = {
        ModbusTable.COIL: 0,
        ModbusTable.DISCRETE_INPUT: 10000,
        ModbusTable.INPUT_REGISTER: 30000,
        ModbusTable.HOLDING_REGISTER: 40000
    }
    prefix = base.get(table, 40000)
    return str(prefix + address)

def get_conversion_formula(tag: Tag) -> str:
    if tag.data_type == DataType.BOOL:
        return "value = Boolean(msg.payload[0])"
    
    if not tag.modbus or tag.modbus.scale == 1.0:
        return "value = msg.payload[0]"
    
    scale = tag.modbus.scale
    return f"raw = msg.payload[0]\nvalue = raw / {scale}"

def is_writable(tag: Tag) -> bool:
    writable_types = [TagType.COMMAND, TagType.ANALOG_OUTPUT, TagType.DIGITAL_OUTPUT]
    writable_tables = [ModbusTable.COIL, ModbusTable.HOLDING_REGISTER]
    
    return tag.tag_type in writable_types and tag.modbus and tag.modbus.table in writable_tables

def build_node_red_tooltip(tag: Tag, server_config: ModbusServerConfig) -> str:
    if not tag.modbus:
        return f"Tag: {tag.name}\n(Sem configuração Modbus)"

    mb = tag.modbus
    unit_id = server_config.unit_id
    read_fc = get_read_fc_for_table(mb.table)
    nr_address = get_node_red_address(mb.address)
    conv_address = get_conventional_address(mb.table, mb.address)
    formula = get_conversion_formula(tag)
    
    lines = []
    lines.append("<b>Node-RED Modbus-Read</b>")
    lines.append(f"Nome: {tag.name}")
    lines.append(f"Tópico: {tag.name}")
    lines.append(f"Unit-Id: {unit_id}")
    lines.append(f"FC: {read_fc}")
    lines.append(f"Endereço configurado: {conv_address}")
    lines.append(f"Address Node-RED: {nr_address}")
    lines.append("Quantity: 1")
    lines.append("Poll Rate: 1000 millisecond(s)")
    lines.append("Server: simuladorServer")
    lines.append("")
    
    if is_writable(tag):
        write_fc = get_write_fc_for_table(mb.table)
        lines.append("<b>Node-RED Modbus-Write</b>")
        lines.append(f"Nome: Escrever {tag.name}")
        lines.append(f"Unit-Id: {unit_id}")
        lines.append(f"FC escrita: {write_fc}")
        lines.append(f"Address Node-RED: {nr_address}")
        lines.append("Value: true ou valor desejado")
        lines.append("Server: simuladorServer")
        lines.append("")

    lines.append("<b>Conversão</b>")
    lines.append(formula.replace("\n", "<br>"))
    if tag.unit:
        lines.append(f"Unidade: {tag.unit}")
    lines.append("")
    
    lines.append("<b>Servidor</b>")
    lines.append(f"Host: {server_config.host}")
    lines.append(f"Porta: {server_config.port}")
    
    return "<br>".join(lines)

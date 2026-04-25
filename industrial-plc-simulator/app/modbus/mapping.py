from typing import List, Dict
from app.domain.models import Tag
from app.modbus.register_store import PLCDataStore

class ModbusMapper:
    def __init__(self, data_store: PLCDataStore):
        self.data_store = data_store

    def update_modbus_from_tags(self, tags: List[Tag]):
        for tag in tags:
            if not tag.modbus:
                continue
                
            val = tag.current_value
            if val is None:
                continue
                
            # Apply scale
            if isinstance(val, (int, float)):
                val = val * tag.modbus.scale
            
            self.data_store.set_value(
                tag.modbus.table.value,
                tag.modbus.address,
                val
            )

    def update_tags_from_modbus(self, tags: List[Tag]):
        """Updates tags that can be written externally (coils/holding registers)"""
        for tag in tags:
            if not tag.modbus:
                continue
                
            # Only update from modbus if it's a writable table (coil or holding_register)
            if tag.modbus.table.value not in ["coil", "holding_register"]:
                continue
                
            # If it's a command or analog_output, it should be synced back
            if tag.tag_type.value in ["command", "analog_output", "digital_output"]:
                val = self.data_store.get_value(
                    tag.modbus.table.value,
                    tag.modbus.address
                )
                
                # Reverse scale
                if val is not None and isinstance(val, (int, float)):
                    val = val / tag.modbus.scale
                
                if tag.data_type.value == "bool":
                    tag.current_value = bool(val)
                else:
                    tag.current_value = val

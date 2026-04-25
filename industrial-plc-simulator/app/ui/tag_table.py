from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel, QHeaderView
from typing import List
from app.domain.models import Tag, Plant, ModbusServerConfig
from app.ui.node_red_tooltip import build_node_red_tooltip

class TagTable(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Tabela de Tags e Valores:"))
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Equipamento", "Tag", "Valor Atual", "Unidade", "Tabela Modbus", "Endereço"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.tags_refs: List[tuple] = []

    def update_tags(self, plant: Plant, server_config: ModbusServerConfig):
        self.table.setRowCount(0)
        self.tags_refs = []
        
        row = 0
        for area in plant.areas:
            for line in area.lines:
                for equip in line.equipments:
                    for tag in equip.tags:
                        self.table.insertRow(row)
                        
                        tooltip = build_node_red_tooltip(tag, server_config)
                        
                        items = [
                            QTableWidgetItem(equip.name),
                            QTableWidgetItem(tag.name),
                            QTableWidgetItem("-"), # value placeholder
                            QTableWidgetItem(tag.unit or ""),
                            QTableWidgetItem(tag.modbus.table.value if tag.modbus else "-"),
                            QTableWidgetItem(str(tag.modbus.address) if tag.modbus else "-")
                        ]
                        
                        for col, item in enumerate(items):
                            item.setToolTip(tooltip)
                            self.table.setItem(row, col, item)
                        
                        self.tags_refs.append((tag, row))
                        row += 1
        self.refresh_values()

    def refresh_values(self):
        for tag, row in self.tags_refs:
            val_str = str(tag.current_value) if tag.current_value is not None else "-"
            # Round floats for display
            if isinstance(tag.current_value, float):
                val_str = f"{tag.current_value:.2f}"
            self.table.setItem(row, 2, QTableWidgetItem(val_str))

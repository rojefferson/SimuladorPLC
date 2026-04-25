from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QLabel
from app.domain.models import Plant, Area, Line, Equipment, Tag

class PlantTree(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Árvore da Planta:"))
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Estrutura", "Tipo"])
        layout.addWidget(self.tree)

    def populate(self, plant: Plant):
        self.tree.clear()
        root = QTreeWidgetItem(self.tree, [plant.name, "Plant"])
        for area in plant.areas:
            area_item = QTreeWidgetItem(root, [area.name, "Area"])
            for line in area.lines:
                line_item = QTreeWidgetItem(area_item, [line.name, "Line"])
                for equip in line.equipments:
                    equip_item = QTreeWidgetItem(line_item, [equip.name, "Equipment"])
                    for tag in equip.tags:
                        QTreeWidgetItem(equip_item, [tag.name, f"Tag ({tag.tag_type.value})"])
        self.tree.expandAll()

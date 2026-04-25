from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, 
    QDialogButtonBox, QDoubleSpinBox, QSpinBox, QLabel
)
from app.domain.enums import TagType, DataType, ModbusTable, SimulationMode
from app.domain.models import Tag, ModbusConfig, SimulationSettings

class TagEditorDialog(QDialog):
    def __init__(self, parent=None, tag: Tag = None):
        super().__init__(parent)
        self.setWindowTitle("Editar Tag" if tag else "Adicionar Tag")
        self.setMinimumWidth(400)
        
        self.layout = QVBoxLayout(self)
        self.form = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        for t in TagType: self.type_combo.addItem(t.value)
        
        self.data_type_combo = QComboBox()
        for d in DataType: self.data_type_combo.addItem(d.value)
        
        self.unit_edit = QLineEdit()
        
        # Modbus
        self.mb_table_combo = QComboBox()
        for m in ModbusTable: self.mb_table_combo.addItem(m.value)
        self.mb_address_spin = QSpinBox()
        self.mb_address_spin.setRange(0, 65535)
        self.mb_scale_spin = QDoubleSpinBox()
        self.mb_scale_spin.setRange(0.001, 1000.0)
        self.mb_scale_spin.setValue(1.0)
        
        # Simulation
        self.sim_mode_combo = QComboBox()
        for s in SimulationMode: self.sim_mode_combo.addItem(s.value)
        self.sim_min_spin = QDoubleSpinBox()
        self.sim_min_spin.setRange(-1000000, 1000000)
        self.sim_max_spin = QDoubleSpinBox()
        self.sim_max_spin.setRange(-1000000, 1000000)
        self.sim_max_spin.setValue(100.0)
        
        self.form.addRow("Nome:", self.name_edit)
        self.form.addRow("Tipo de Tag:", self.type_combo)
        self.form.addRow("Tipo de Dado:", self.data_type_combo)
        self.form.addRow("Unidade:", self.unit_edit)
        self.form.addRow(QLabel("-- Modbus --"), QLabel(""))
        self.form.addRow("Tabela Modbus:", self.mb_table_combo)
        self.form.addRow("Endereço:", self.mb_address_spin)
        self.form.addRow("Escala:", self.mb_scale_spin)
        self.form.addRow(QLabel("-- Simulação --"), QLabel(""))
        self.form.addRow("Modo Simulação:", self.sim_mode_combo)
        self.form.addRow("Mínimo:", self.sim_min_spin)
        self.form.addRow("Máximo:", self.sim_max_spin)
        
        self.layout.addLayout(self.form)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
        
        if tag:
            self.name_edit.setText(tag.name)
            self.type_combo.setCurrentText(tag.tag_type.value)
            self.data_type_combo.setCurrentText(tag.data_type.value)
            self.unit_edit.setText(tag.unit or "")
            if tag.modbus:
                self.mb_table_combo.setCurrentText(tag.modbus.table.value)
                self.mb_address_spin.setValue(tag.modbus.address)
                self.mb_scale_spin.setValue(tag.modbus.scale)
            if tag.simulation:
                self.sim_mode_combo.setCurrentText(tag.simulation.mode.value)
                self.sim_min_spin.setValue(tag.simulation.min)
                self.sim_max_spin.setValue(tag.simulation.max)

    def get_tag_data(self) -> Tag:
        mb = ModbusConfig(
            table=ModbusTable(self.mb_table_combo.currentText()),
            address=self.mb_address_spin.value(),
            scale=self.mb_scale_spin.value()
        )
        sim = SimulationSettings(
            mode=SimulationMode(self.sim_mode_combo.currentText()),
            min=self.sim_min_spin.value(),
            max=self.sim_max_spin.value(),
            initial_value=None # simplified
        )
        return Tag(
            name=self.name_edit.text(),
            tag_type=TagType(self.type_combo.currentText()),
            data_type=DataType(self.data_type_combo.currentText()),
            unit=self.unit_edit.text(),
            modbus=mb,
            simulation=sim
        )

import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFileDialog, QMessageBox, QLabel, QSplitter
)
from PySide6.QtCore import Qt, QTimer

from app.domain.models import SimulationConfig, Plant, Area, Line, Equipment, ModbusServerConfig
from app.domain.validation import validate_simulation_config
from app.persistence.json_repository import save_simulation, load_simulation
from app.simulation.engine import SimulationEngine
from app.modbus.server import ModbusServer
from app.modbus.register_store import PLCDataStore
from app.modbus.mapping import ModbusMapper
from app.export.tag_map_exporter import export_tag_map

from app.ui.plant_tree import PlantTree
from app.ui.tag_table import TagTable
from app.ui.log_panel import LogPanel
from app.ui.tag_editor import TagEditorDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Industrial PLC Simulator")
        self.resize(1200, 800)
        
        self.config = SimulationConfig("Nova Simulação")
        self.engine = None
        self.modbus_server = None
        self.data_store = PLCDataStore()
        self.mapper = ModbusMapper(self.data_store)
        
        self.setup_ui()
        self.setup_timers()
        self.log_panel.log("Aplicação iniciada.")

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        btn_new = QPushButton("Nova Planta")
        btn_new.clicked.connect(self.new_plant)
        btn_default = QPushButton("Carregar Planta Padrão")
        btn_default.clicked.connect(self.load_default_plant)
        btn_import = QPushButton("Importar JSON")
        btn_import.clicked.connect(self.import_json)
        btn_save = QPushButton("Salvar JSON")
        btn_save.clicked.connect(self.save_json)
        btn_export_map = QPushButton("Exportar Mapa de Tags")
        btn_export_map.clicked.connect(self.export_map)
        
        btn_add_equip = QPushButton("Adicionar Equipamento")
        btn_add_equip.clicked.connect(self.add_equipment)
        btn_add_tag = QPushButton("Adicionar Tag")
        btn_add_tag.clicked.connect(self.add_tag)
        
        toolbar_layout.addWidget(btn_new)
        toolbar_layout.addWidget(btn_default)
        toolbar_layout.addWidget(btn_import)
        toolbar_layout.addWidget(btn_save)
        toolbar_layout.addWidget(btn_export_map)
        toolbar_layout.addWidget(btn_add_equip)
        toolbar_layout.addWidget(btn_add_tag)
        toolbar_layout.addStretch()
        
        self.btn_toggle_sim = QPushButton("Iniciar Simulação")
        self.btn_toggle_sim.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 5px;")
        self.btn_toggle_sim.clicked.connect(self.toggle_simulation)
        
        toolbar_layout.addWidget(self.btn_toggle_sim)
        
        main_layout.addLayout(toolbar_layout)
        
        # Main Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Tree
        self.plant_tree = PlantTree()
        splitter.addWidget(self.plant_tree)
        
        # Right: Table and Logs
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        
        self.tag_table = TagTable()
        right_layout.addWidget(self.tag_table, 3)
        
        self.log_panel = LogPanel()
        right_layout.addWidget(self.log_panel, 1)
        
        splitter.addWidget(right_container)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        
        # Status Bar
        self.status_label = QLabel("Status: Parado | Modbus: Desconectado")
        self.statusBar().addWidget(self.status_label)

    def setup_timers(self):
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.on_refresh_tick)
        self.refresh_timer.start(500) # 500ms UI refresh

    def on_refresh_tick(self):
        if self.engine and self.engine.running:
            # Sync Tags <-> Modbus
            all_tags = []
            for area in self.config.plant.areas:
                for line in area.lines:
                    for equip in line.equipments:
                        all_tags.extend(equip.tags)
            
            # Sync from tags to Modbus (for simulator updates)
            self.mapper.update_modbus_from_tags(all_tags)
            
            # Sync from Modbus back to tags (for external writes)
            self.mapper.update_tags_from_modbus(all_tags)
            
            # Refresh UI
            self.tag_table.refresh_values()

    def load_default_plant(self):
        default_path = os.path.join(os.getcwd(), "examples", "default_plant.json")
        if os.path.exists(default_path):
            try:
                self.config = load_simulation(default_path)
                self.update_ui_from_config()
                self.log_panel.log("Planta padrão carregada com sucesso.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao carregar planta padrão: {e}")
        else:
            QMessageBox.warning(self, "Aviso", "Arquivo de planta padrão não encontrado em examples/default_plant.json")

    def new_plant(self):
        self.config = SimulationConfig("Nova Simulação")
        self.update_ui_from_config()
        self.log_panel.log("Nova planta criada.")

    def import_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importar Simulação", "", "JSON Files (*.json)")
        if path:
            try:
                self.config = load_simulation(path)
                self.update_ui_from_config()
                self.log_panel.log(f"Simulação importada de {path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao importar JSON: {e}")

    def save_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Simulação", "", "JSON Files (*.json)")
        if path:
            try:
                save_simulation(self.config, path)
                self.log_panel.log(f"Simulação salva em {path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao salvar JSON: {e}")

    def export_map(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar Mapa de Tags", "tag_map.json", "JSON Files (*.json)")
        if path:
            try:
                export_tag_map(self.config, path)
                self.log_panel.log(f"Mapa de tags exportado para {path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao exportar mapa: {e}")

    def update_ui_from_config(self):
        self.plant_tree.populate(self.config.plant)
        self.tag_table.update_tags(self.config.plant, self.config.modbus_server)
        self.status_label.setText(f"Status: Parado | Modbus: {self.config.modbus_server.host}:{self.config.modbus_server.port}")

    def toggle_simulation(self):
        is_running = self.engine and self.engine.running
        if is_running:
            self.stop_simulation()
            self.btn_toggle_sim.setText("Iniciar Simulação")
            self.btn_toggle_sim.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 5px;")
        else:
            self.start_simulation()
            if self.engine and self.engine.running:
                self.btn_toggle_sim.setText("Parar Simulação")
                self.btn_toggle_sim.setStyleSheet("background-color: #c62828; color: white; font-weight: bold; padding: 5px;")

    def start_simulation(self):
        errors = validate_simulation_config(self.config)
        if errors:
            QMessageBox.warning(self, "Validação", "\n".join(errors))
            return
            
        self.engine = SimulationEngine(self.config)
        self.engine.start()
        
        self.modbus_server = ModbusServer(
            self.data_store, 
            self.config.modbus_server.host, 
            self.config.modbus_server.port
        )
        self.modbus_server.start()
        
        self.status_label.setText(f"Status: RODANDO | Modbus: {self.config.modbus_server.host}:{self.config.modbus_server.port}")
        self.log_panel.log("Simulação iniciada.")

    def stop_simulation(self):
        if self.engine:
            self.engine.stop()
        if self.modbus_server:
            self.modbus_server.stop()
            
        self.status_label.setText(f"Status: Parado | Modbus: {self.config.modbus_server.host}:{self.config.modbus_server.port}")
        self.log_panel.log("Simulação parada.")

    def add_equipment(self):
        if not self.config.plant.areas:
            # Create a default area if none exists
            self.config.plant.areas.append(Area("producao"))
        if not self.config.plant.areas[0].lines:
            self.config.plant.areas[0].lines.append(Line("linha_01"))
            
        line = self.config.plant.areas[0].lines[0]
        name = f"Equipamento_{len(line.equipments) + 1}"
        line.equipments.append(Equipment(name))
        self.update_ui_from_config()
        self.log_panel.log(f"Equipamento '{name}' adicionado.")

    def add_tag(self):
        # Add tag to the first equipment for simplicity in this version
        found_equip = None
        for area in self.config.plant.areas:
            for line in area.lines:
                if line.equipments:
                    found_equip = line.equipments[0]
                    break
            if found_equip: break
            
        if not found_equip:
            QMessageBox.warning(self, "Aviso", "Crie um equipamento antes de adicionar uma tag.")
            return
            
        dialog = TagEditorDialog(self)
        if dialog.exec():
            new_tag = dialog.get_tag_data()
            found_equip.tags.append(new_tag)
            self.update_ui_from_config()
            self.log_panel.log(f"Tag '{new_tag.name}' adicionada ao equipamento '{found_equip.name}'.")

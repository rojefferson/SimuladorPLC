import time
import threading
from typing import Dict, List, Optional
from app.domain.models import SimulationConfig, Tag
from app.domain.enums import SimulationMode
from app.simulation.value_generators import (
    generate_constant, generate_random, generate_random_walk,
    generate_counter, generate_state
)
from app.simulation.rules import apply_default_rules

class SimulationEngine:
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.tags: List[Tag] = []
        self.tags_by_name: Dict[str, Tag] = {}
        self._initialize_tags()
        
    def _initialize_tags(self):
        self.tags = []
        self.tags_by_name = {}
        for area in self.config.plant.areas:
            for line in area.lines:
                for equipment in line.equipments:
                    for tag in equipment.tags:
                        self.tags.append(tag)
                        self.tags_by_name[tag.name] = tag
                        if tag.current_value is None and tag.simulation:
                            tag.current_value = tag.simulation.initial_value

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def _run(self):
        while self.running:
            self._update_values()
            time.sleep(1.0) # 1 second tick

    def _update_values(self):
        for tag in self.tags:
            if not tag.simulation:
                continue
                
            mode = tag.simulation.mode
            
            if mode == SimulationMode.CONSTANT:
                tag.current_value = generate_constant(tag)
            elif mode == SimulationMode.RANDOM:
                tag.current_value = generate_random(tag)
            elif mode == SimulationMode.RANDOM_WALK:
                tag.current_value = generate_random_walk(tag)
            elif mode == SimulationMode.COUNTER:
                # Basic counter if not handled by rules
                if not self.config.simulation_name == "Linha de Envase Padrão":
                    tag.current_value = generate_counter(tag)
            elif mode == SimulationMode.STATE:
                tag.current_value = generate_state(tag)
            elif mode == SimulationMode.COMMAND:
                # Commands are usually written from outside, but we can ensure they have a value
                if tag.current_value is None:
                    tag.current_value = tag.simulation.initial_value
            # RULE, FAULT, etc. handled separately or by rules engine
            
        # Apply specific rules
        if self.config.simulation_name == "Linha de Envase Padrão":
            apply_default_rules(self.config, self.tags_by_name)

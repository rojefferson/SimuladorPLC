import random
from typing import Any
from app.domain.models import Tag

def generate_constant(tag: Tag) -> Any:
    if tag.current_value is None:
        return tag.simulation.initial_value if tag.simulation else 0
    return tag.current_value

def generate_random(tag: Tag) -> Any:
    sim = tag.simulation
    if not sim:
        return 0
    
    if tag.data_type.value == "bool":
        return random.choice([True, False])
    
    val = random.uniform(sim.min, sim.max)
    if tag.data_type.value == "int":
        return int(val)
    return val

def generate_random_walk(tag: Tag) -> Any:
    sim = tag.simulation
    if not sim:
        return 0
        
    current = tag.current_value
    if current is None:
        current = sim.initial_value if sim.initial_value is not None else (sim.min + sim.max) / 2
        
    step = (sim.max - sim.min) * 0.05  # 5% of range
    variation = random.uniform(-step, step)
    new_val = current + variation
    
    # Keep within bounds
    new_val = max(sim.min, min(sim.max, new_val))
    
    if tag.data_type.value == "int":
        return int(new_val)
    return new_val

def generate_counter(tag: Tag) -> Any:
    sim = tag.simulation
    if not sim:
        return 0
        
    current = tag.current_value
    if current is None:
        current = sim.initial_value if sim.initial_value is not None else 0
        
    new_val = current + 1
    if new_val > sim.max:
        new_val = sim.min
        
    return int(new_val)

def generate_state(tag: Tag) -> bool:
    if tag.current_value is None:
        return tag.simulation.initial_value if tag.simulation else False
    return tag.current_value

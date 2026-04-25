import time
import os
from app.persistence.json_repository import load_simulation
from app.simulation.engine import SimulationEngine

def debug_sim():
    # 1. Load default plant
    plant_path = os.path.join(os.getcwd(), "examples", "default_plant.json")
    print(f"Loading plant from {plant_path}...")
    config = load_simulation(plant_path)
    
    # 2. Setup Engine
    print("Starting Simulation Engine...")
    engine = SimulationEngine(config)
    engine.start()
    
    # 3. Monitor values for 5 seconds
    print("\nMonitoring values for 5 seconds:")
    print("-" * 50)
    for i in range(5):
        time.sleep(1)
        print(f"Tick {i+1}:")
        for tag in engine.tags:
            if tag.name in ["MotorLigado", "ContadorGarrafas", "NivelTanque", "VelocidadeRPM"]:
                print(f"  {tag.name}: {tag.current_value}")
        print("-" * 50)
    
    engine.stop()
    print("Simulation stopped.")

if __name__ == "__main__":
    debug_sim()

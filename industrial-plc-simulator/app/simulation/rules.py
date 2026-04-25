from typing import Dict, Any
from app.domain.models import SimulationConfig, Tag
from app.domain.enums import SimulationMode

def apply_default_rules(config: SimulationConfig, tags_by_name: Dict[str, Tag]):
    """
    Applies logic rules for the 'Linha de Envase Padrão'.
    """
    # 1. Start / Stop logic
    start = tags_by_name.get("Start")
    stop = tags_by_name.get("Stop")
    motor_ligado = tags_by_name.get("MotorLigado")
    bomba_ligada = tags_by_name.get("BombaLigada")
    
    if start and start.current_value:
        if motor_ligado: motor_ligado.current_value = True
        if bomba_ligada: bomba_ligada.current_value = True
        start.current_value = False # Auto-reset
        
    if stop and stop.current_value:
        if motor_ligado: motor_ligado.current_value = False
        if bomba_ligada: bomba_ligada.current_value = False
        stop.current_value = False # Auto-reset

    # 3 & 4. VelocidadeRPM logic
    velocidade = tags_by_name.get("VelocidadeRPM")
    if velocidade and motor_ligado:
        if motor_ligado.current_value:
            # Tend to 1300 (mid of 800-1800)
            target = 1300.0
            current = velocidade.current_value or 0
            velocidade.current_value = current + (target - current) * 0.1
        else:
            # Tend to 0
            current = velocidade.current_value or 0
            velocidade.current_value = current * 0.8
            if velocidade.current_value < 1: velocidade.current_value = 0

    # 5. ContadorGarrafas
    contador = tags_by_name.get("ContadorGarrafas")
    if contador and motor_ligado and motor_ligado.current_value:
        from app.simulation.value_generators import generate_counter
        contador.current_value = generate_counter(contador)

    # 7. AlarmeSobrecarga
    temp_motor = tags_by_name.get("TemperaturaMotor")
    alarme_sobrecarga = tags_by_name.get("AlarmeSobrecarga")
    if temp_motor and alarme_sobrecarga:
        if temp_motor.current_value > 80:
            alarme_sobrecarga.current_value = True

    # 8 & 9. Tanque Alarms
    nivel = tags_by_name.get("NivelTanque")
    alarme_baixo = tags_by_name.get("AlarmeNivelBaixo")
    alarme_alto = tags_by_name.get("AlarmeNivelAlto")
    if nivel:
        if alarme_baixo: alarme_baixo.current_value = (nivel.current_value < 20)
        if alarme_alto: alarme_alto.current_value = (nivel.current_value > 90)

    # 10. Reset
    reset = tags_by_name.get("Reset")
    if reset and reset.current_value:
        # Clear alarms if conditions met
        if alarme_sobrecarga and temp_motor and temp_motor.current_value <= 80:
            alarme_sobrecarga.current_value = False
        if alarme_baixo and nivel and nivel.current_value >= 20:
            alarme_baixo.current_value = False
        if alarme_alto and nivel and nivel.current_value <= 90:
            alarme_alto.current_value = False
        reset.current_value = False

    # 12. SensorPresenca
    sensor_presenca = tags_by_name.get("SensorPresenca")
    if sensor_presenca and motor_ligado and motor_ligado.current_value:
        import random
        if random.random() > 0.7:
            sensor_presenca.current_value = not sensor_presenca.current_value

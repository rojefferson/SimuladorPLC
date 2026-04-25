from pymodbus.client import ModbusTcpClient
import sys

def test_connection():
    print("Tentando conectar ao simulador em 127.0.0.1:5020...")
    client = ModbusTcpClient('127.0.0.1', port=5020)
    
    try:
        if not client.connect():
            print("ERRO: Nao foi possivel conectar ao servidor Modbus.")
            return

        # Lendo Coil 1 (MotorLigado)
        print("Lendo Coil 1 (MotorLigado)...")
        result = client.read_coils(1, count=1, device_id=1)
        
        if result.isError():
            print(f"ERRO Modbus ao ler Coil 1: {result}")
        else:
            print(f"SUCESSO! Valor do MotorLigado: {result.bits[0]}")

        # Lendo Holding Register 20 (ContadorGarrafas)
        print("Lendo Holding Register 20 (ContadorGarrafas)...")
        result = client.read_holding_registers(20, count=1, device_id=1)
        
        if result.isError():
            print(f"ERRO Modbus ao ler Register 20: {result}")
        else:
            print(f"SUCESSO! Valor do ContadorGarrafas: {result.registers[0]}")

    except Exception as e:
        print(f"Ocorreu uma excecao: {e}")
    finally:
        client.close()
        print("Conexao encerrada.")

if __name__ == "__main__":
    test_connection()

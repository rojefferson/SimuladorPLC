from pymodbus.datastore import ModbusServerContext
from pymodbus.constants import ExcCodes
from typing import Dict, Any, List, Union
import logging

# Configuração de logging para depuração
logger = logging.getLogger(__name__)

class PLCDataStore(ModbusServerContext):
    """
    Um datastore customizado que atua como uma ponte direta entre o simulador 
    e o servidor Modbus, eliminando problemas de sincronização do PyModbus 3.x.
    """
    def __init__(self):
        # Inicializa a estrutura de memória direta
        self.storage = {
            "coil": [False] * 1000,
            "discrete_input": [False] * 1000,
            "input_register": [0] * 1000,
            "holding_register": [0] * 1000
        }
        
        # Mapeamento de Function Codes para tabelas
        self.fc_map = {
            1: "coil",
            2: "discrete_input",
            3: "holding_register",
            4: "input_register",
            5: "coil",
            6: "holding_register",
            15: "coil",
            16: "holding_register"
        }

        # Necessário para o ModbusServerContext e StartTcpServer
        self._devices = {0: self}
        self.simdevices = [] # Evita que o PyModbus envolva em SimCore
        
    async def async_getValues(self, unit_id: int, fc: int, address: int, count: int = 1) -> Union[List[Any], ExcCodes]:
        """Chamado pelo servidor Modbus para ler dados."""
        table = self.fc_map.get(fc)
        if not table:
            return ExcCodes.ILLEGAL_FUNCTION
            
        # Ajuste de endereço (Protocolo Modbus é 0-based, nossa planta é 1-based)
        # Se o usuário pede endereço 30 no Node-RED, e nossa planta usa 30,
        # dependendo do cliente Node-RED, ele pode estar pedindo 30 ou 29.
        # Vamos assumir que o endereço passado aqui é o endereço do protocolo.
        # Se nossa planta diz 30, e o Node-RED pede 30, acessamos o índice 30.
        
        try:
            data_list = self.storage[table]
            if 0 <= address < len(data_list):
                result = data_list[address:address + count]
                # logger.debug(f"Modbus Read: {table} @ {address} (count {count}) -> {result}")
                return result
            else:
                return ExcCodes.ILLEGAL_ADDRESS
        except Exception as e:
            logger.error(f"Erro na leitura Modbus: {e}")
            return ExcCodes.FAILURE

    async def async_setValues(self, unit_id: int, fc: int, address: int, values: List[Any]) -> Union[None, ExcCodes]:
        """Chamado pelo servidor Modbus para escrever dados (comandos)."""
        table = self.fc_map.get(fc)
        if not table:
            return ExcCodes.ILLEGAL_FUNCTION
            
        try:
            data_list = self.storage[table]
            count = len(values)
            if 0 <= address < len(data_list):
                for i in range(count):
                    if address + i < len(data_list):
                        data_list[address + i] = values[i]
                
                # Log de comando recebido
                print(f"[MODBUS] Comando recebido: {table} @ {address} -> {values}")
                return None
            else:
                return ExcCodes.ILLEGAL_ADDRESS
        except Exception as e:
            logger.error(f"Erro na escrita Modbus: {e}")
            return ExcCodes.FAILURE

    def set_value(self, table: str, address: int, value: Any):
        """Método usado pelo simulador para atualizar valores."""
        if table in self.storage:
            # Aqui fazemos o ajuste: se a planta diz endereço 30, gravamos no índice 30
            # para que se o Node-RED pedir 30, ele ache.
            if 0 <= address < len(self.storage[table]):
                # Converter para o tipo correto do Modbus
                if table in ["coil", "discrete_input"]:
                    final_val = bool(value)
                else:
                    final_val = int(value)
                
                self.storage[table][address] = final_val
                # logger.debug(f"Direct Store Update: {table} @ {address} -> {final_val}")

    def get_value(self, table: str, address: int) -> Any:
        """Método usado pelo simulador para ler valores."""
        if table in self.storage:
            if 0 <= address < len(self.storage[table]):
                return self.storage[table][address]
        return None

    @property
    def context(self):
        """Retorna a si mesmo como contexto do servidor."""
        return self

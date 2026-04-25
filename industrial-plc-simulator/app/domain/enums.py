from enum import Enum

class TagType(Enum):
    DIGITAL_INPUT = "digital_input"
    DIGITAL_OUTPUT = "digital_output"
    ANALOG_INPUT = "analog_input"
    ANALOG_OUTPUT = "analog_output"
    COUNTER = "counter"
    ALARM = "alarm"
    COMMAND = "command"
    STATUS = "status"

class DataType(Enum):
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    STRING = "string"

class ModbusTable(Enum):
    COIL = "coil"
    DISCRETE_INPUT = "discrete_input"
    HOLDING_REGISTER = "holding_register"
    INPUT_REGISTER = "input_register"

class SimulationMode(Enum):
    CONSTANT = "constant"
    RANDOM = "random"
    RANDOM_WALK = "random_walk"
    COUNTER = "counter"
    STATE = "state"
    RULE = "rule"
    COMMAND = "command"
    FAULT = "fault"
    COMMUNICATION_LOSS = "communication_loss"

from enum import Enum


class MovementType(Enum):
    INBOUND = "ENTRADA"
    OUTBOUND = "SAÍDA"


class BeverageCategory(Enum):
    BEER = "CERVEJA"
    SODA = "REFRIGERANTE"
    JUICE = "SUCO"


import random
from .base import VariableAleatoria

class VariableExponencial(VariableAleatoria):
    def __init__(self, nombre: str, lambd: float):
        super().__init__(nombre)
        self.lambd = lambd

    def muestrear(self) -> float:
        return random.expovariate(self.lambd)
    #este metodo mide el tiempo entre goles de cada equipo
    #con lambda recibe la tasa de goles esperados 
    
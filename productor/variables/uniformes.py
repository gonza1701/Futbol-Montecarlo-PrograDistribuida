import random
from .base import VariableAleatoria

# Modula factores totalmente neutrales y de igual probabilidad, como las decisiones del VAR
class VariableUniforme(VariableAleatoria):
    def __init__(self, nombre: str, minimo: float, maximo: float):
        super().__init__(nombre)
        self.minimo = minimo # limite inferior del factor aleatorio
        self.maximo = maximo # limite superior del factor aleatorio

    def muestrear(self) -> float:
        #genera probabilidades uniformes entre el minimo y el maximo
        return random.uniform(self.minimo, self.maximo)
    
import random
from .base import VariableAleatoria

class VariableNormal(VariableAleatoria):
    def __init__(self, nombre: str, mu: float, sigma: float):
        super().__init__(nombre)
        self.mu = mu #media 
        self.sigma = sigma #desviación estándar 

    def muestrear(self) -> float:
        return random.gauss(self.mu, self.sigma)
        #genera valoores flotantes basados en mu y sigma 
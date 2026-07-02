from abc import ABC, abstractmethod

class VariableAleatoria(ABC):
    def __init__(self, nombre: str):
        self.nombre = nombre

    @abstractmethod
    def muestrear(self) -> float:
        #Genera un valor aleatorio siguiendo la distribucion.
        pass
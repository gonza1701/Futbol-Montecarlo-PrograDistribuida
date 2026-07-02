import os
from variables.exponenciales import VariableExponencial
from variables.normales import VariableNormal
from variables.uniformes import VariableUniforme

class ModeloFutbol:
    def __init__(self, id_modelo: str):
        self.id_modelo = id_modelo
        self.variables = {}

    def agregar_variable(self, variable):
        self.variables[variable.nombre] = variable

    def generar_escenario_dict(self) -> dict:
        return {nombre: var.muestrear() for nombre, var in self.variables.items()}

    @staticmethod
    def cargar_desde_archivo(ruta_archivo: str) -> 'ModeloFutbol':
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"No se encontró el archivo de modelo en: {ruta_archivo}")
            
        id_modelo = os.path.basename(ruta_archivo).replace(".txt", "")
        modelo = ModeloFutbol(id_modelo)
        
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                
                partes = linea.split(",")
                nombre = partes[0]
                distribucion = partes[1].lower()
                
                if distribucion == "exponencial":
                    modelo.agregar_variable(VariableExponencial(nombre, float(partes[2])))
                elif distribucion == "normal":
                    modelo.agregar_variable(VariableNormal(nombre, float(partes[2]), float(partes[3])))
                elif distribucion == "uniforme":
                    modelo.agregar_variable(VariableUniforme(nombre, float(partes[2]), float(partes[3])))
                    
        return modelo
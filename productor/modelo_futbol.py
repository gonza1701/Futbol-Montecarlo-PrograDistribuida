import os
from variables.exponenciales import VariableExponencial
from variables.normales import VariableNormal
from variables.uniformes import VariableUniforme
'''
Agrupacion de variables aleatorias para el modelo de futbol. Permite agregar variables y generar escenarios de manera sencilla.
'''
class ModeloFutbol:
    def __init__(self, id_modelo: str):
        self.id_modelo = id_modelo
        self.variables = {} # Permite indexar las variables por su nombre

    def agregar_variable(self, variable):
        self.variables[variable.nombre] = variable  

    def generar_escenario_dict(self) -> dict:
        return {nombre: var.muestrear() for nombre, var in self.variables.items()}
    #muestra todas las continuas del modelo 

    """
    Parser de texto
    Toma el archivo .txt y limpia lineas vacias y comentarios, luego separa por comas e instancia la jerarquia de objetos.
    """

    @staticmethod
    def cargar_desde_archivo(ruta_archivo: str) -> 'ModeloFutbol':
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"No se encontró el archivo de modelo en: {ruta_archivo}")
            
        id_modelo = os.path.basename(ruta_archivo).replace(".txt", "")
        modelo = ModeloFutbol(id_modelo)
        
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                #Ignora lineas vacias 
                if not linea or linea.startswith("#"):
                    continue
                #Tokeniza la linea 
                partes = linea.split(",")
                nombre = partes[0]
                distribucion = partes[1].lower()
                
                #Mapeo dinamico a las clases de distribucion
                if distribucion == "exponencial":
                    modelo.agregar_variable(VariableExponencial(nombre, float(partes[2])))
                elif distribucion == "normal":
                    modelo.agregar_variable(VariableNormal(nombre, float(partes[2]), float(partes[3])))
                elif distribucion == "uniforme":
                    modelo.agregar_variable(VariableUniforme(nombre, float(partes[2]), float(partes[3])))
                    
        return modelo
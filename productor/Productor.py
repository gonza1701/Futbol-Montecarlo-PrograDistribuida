# productor/Productor.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common.middleware import ConectorRabbitMQ
from common import futbol_mensajes_pb2
import time

def test_productor_docker():
    print("Iniciando Productor desde contenedor Docker...")
    time.sleep(2) 
    
    conector = ConectorRabbitMQ()
    print("Conectado exitosamente al bróker desde el contenedor")
    conector.cerrar()

if __name__ == '__main__':
    test_productor_docker()
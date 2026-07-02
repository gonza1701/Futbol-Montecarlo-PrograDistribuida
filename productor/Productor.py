import sys
import os
import time
import uuid



# Asegura que Python encuentre tus variables locales y la carpeta common/

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modelo_futbol import ModeloFutbol
from common.middleware import ConectorRabbitMQ, SerializadorProtobuf

# Importamos las clases generadas por el compilador de protocol buffers
import common.futbol_mensajes_pb2 as pb2

def ejecutar_productor_distribuido():
    print(" Productor: Inicializando nodo emisor de simulación...")

    #conexion a rabbitmq

    try:
        conector = ConectorRabbitMQ()
        print("Conexión establecida con RabbitMQ con éxito.")
    except Exception as e:
        print(f" Error crítico al conectar a RabbitMQ: {e}")
        print("Revisa que el contenedor Docker esté encendido y el .env configurado.")
        return

    # Carga el parser y el modelo base desde el archivo de texto
    ruta_txt = os.path.join(os.path.dirname(__file__), 'modelo', 'modelo_base.txt')
    try:
        modelo = ModeloFutbol.cargar_desde_archivo(ruta_txt)
        print(f" [Parser] Archivo '{modelo.id_modelo}.txt' parseado e interpretado correctamente.")
    except Exception as e:
        print(f" Error en el Parser: {e}")
        conector.cerrar()
        return

    try:
        # Limpiamos los mensajes anteriores 
        conector.purgar_cola('cola_modelo')
        
        # Instanciar la clase definida en el .proto para el contrato de modelo
        msg_modelo = pb2.ModeloFutbol()
        msg_modelo.id_modelo = modelo.id_modelo
        msg_modelo.formula_evaluacion = "evaluacion_montecarlo_basica"
        
        # Construimos la estructura repetida con el bloque oneof para cada distribución
        for nombre, var in modelo.variables.items():
            var_proto = pb2.VariableAleatoria()
            var_proto.nombre = nombre
            
            tipo_var = type(var).__name__
            
            if tipo_var == "VariableExponencial":
                # Usamos setattr para asignarlo de forma segura porque 'lambda' es palabra reservada en Python
                exp_msg = getattr(var_proto, "exponencial")
                setattr(exp_msg, "lambda", var.lambd)
            elif tipo_var == "VariableNormal":
                var_proto.normal.mu = var.mu
                var_proto.normal.sigma = var.sigma
            elif tipo_var == "VariableUniforme":
                var_proto.uniforme.min = var.minimo
                var_proto.uniforme.max = var.maximo
                
            msg_modelo.variables.append(var_proto)

        # Serializamos usando el metodo estático  
        payload_modelo_binario = SerializadorProtobuf.serializar(msg_modelo)
        
        # metodo publicar en la cola de RabbitMQ
        conector.publicar_en_cola('cola_modelo', payload_modelo_binario)
        print("Contrato 'ModeloFutbol' publicado en 'cola_modelo'.")
        
    except Exception as e:
        print(f" Advertencia al publicar el contrato base: {e}")
        print("Saltando directo al bucle de escenarios continuos...")

    # 
    # Bucle de simulacion (Modelo montecarlo) para generar escenarios de partidos de fútbol
    
    print("\nIniciando flujo continuo de escenarios. Presiona Ctrl+C para detener la ráfaga.")
    total_enviados = 0
    
    try:
        while True:
            # Generación de identificador único global para el escenario
            id_escenario = str(uuid.uuid4())
            
            # Motor matematico generando muestras aleatorias para el escenario de partido
            valores = modelo.generar_escenario_dict()
            
            # Instanciamos la estructura exacta del .proto para EscenarioPartido
            msg_escenario = pb2.EscenarioPartido()
            msg_escenario.id_escenario = id_escenario
            
            #Asignacion de las variables generadas por el motor matemático a los campos del mensaje Protobuf
            msg_escenario.t_gol_local = valores.get('t_gol_local', 0.0)
            msg_escenario.t_gol_visitante = valores.get('t_gol_visitante', 0.0)
            msg_escenario.rendimiento_local = valores.get('rendimiento_local', 0.0)
            msg_escenario.rendimiento_visitante = valores.get('rendimiento_visitante', 0.0)
            msg_escenario.factor_var = valores.get('factor_var', 0.0)
            
            # serializamos el mensaje de escenario usando el método estático de SerializadorProtobuf
            payload_binario = SerializadorProtobuf.serializar(msg_escenario)
            
            # metodo publicar 
            conector.publicar_en_cola('cola_escenarios', payload_binario)
            
            total_enviados += 1
            if total_enviados % 1000 == 0:
                print(f"Estatus: {total_enviados} escenarios continuos inyectados con éxito...")
            
            # Pausa de control de flujo para regular los sockets de red (1 milisegundo)
            time.sleep(0.001)

    except KeyboardInterrupt:
        print("\nTransmisión pausada por el operador (Productor detenido manualmente).")
    finally:
        # Cierre seguro del canal y conexión a la red 
        conector.cerrar()
        print("Conexión con RabbitMQ liberada de forma segura.")

if __name__ == "__main__":
    ejecutar_productor_distribuido()
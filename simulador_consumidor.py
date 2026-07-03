import sys
import os
import random

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from common.middleware import ConectorRabbitMQ, SerializadorProtobuf
from common.futbol_mensajes_pb2 import EscenarioPartido, ResultadoPartido, EventoEstadistica

def iniciar_consumidor_falso():
    conector = ConectorRabbitMQ()
    print("[Consumidor Falso] Conectado y esperando escenarios...")
    
    estado = {"procesados": 0, "victorias_local": 0}

    def procesar_escenario(ch, method, properties, body):
        # 1. Leer el escenario que envió el Productor
        escenario = SerializadorProtobuf.deserializar(body, EscenarioPartido)
        
        # 2. Simular el modelo de Montecarlo (Goles al azar)
        goles_l = random.randint(0, 4)
        goles_v = random.randint(0, 3)
        gana_local = goles_l > goles_v
        
        if gana_local: 
            estado["victorias_local"] += 1
        estado["procesados"] += 1

        # 3. Empaquetar y enviar el Resultado a la gráfica de pastel y tabla
        res = ResultadoPartido(
            id_escenario=escenario.id_escenario,
            gana_local=gana_local,
            goles_local=goles_l,
            goles_visitante=goles_v
        )
        conector.publicar_en_cola('cola_resultados', SerializadorProtobuf.serializar(res))

        # 4. Empaquetar y enviar la Estadística (cada 10 mensajes para que sea fluido)
        if estado["procesados"] % 10 == 0:
            probabilidad = (estado["victorias_local"] / estado["procesados"]) * 100
            est = EventoEstadistica(
                origen="consumidor-1",
                tasa_por_segundo=random.uniform(150.0, 250.0),
                probabilidad_victoria_local_acumulada=probabilidad,
                escenarios_procesados=estado["procesados"]
            )
            conector.publicar_en_exchange('exchange_estadisticas', SerializadorProtobuf.serializar(est))

        # 5. Confirmar a RabbitMQ que la caja fue procesada
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Iniciar la escucha
    conector.consumir('cola_escenarios', procesar_escenario)
    conector.iniciar_consumo()

if __name__ == '__main__':
    iniciar_consumidor_falso()
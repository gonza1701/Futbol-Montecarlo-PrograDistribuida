import argparse
import os
import sys
import time

# Asegura que Python encuentre tus variables locales y la carpeta common/
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.middleware import ConectorRabbitMQ, SerializadorProtobuf
import common.futbol_mensajes_pb2 as pb2
from evaluadores import REGISTRO_EVALUADORES


class Consumidor:
    def __init__(self, conector: ConectorRabbitMQ, id_consumidor: str):
        self.conector = conector
        self.id_consumidor = id_consumidor
        self.formula_evaluacion = None

        # Contadores globales (desde que arranco este Consumidor).
        self.escenarios_procesados = 0
        self.victorias_local = 0

        # Contadores de la ventana actual, para calcular throughput
        # (escenarios/seg) desde el ultimo reporte de estadisticas.
        self._inicio_ventana = time.time()
        self._procesados_ventana = 0

    # leer el modelo una sola vez

    def cargar_modelo(self, timeout=30):
        canal = self.conector.canal
        limite = time.time() + timeout
        metodo = cuerpo = None

        while time.time() < limite:
            metodo, _props, cuerpo = canal.basic_get(queue='cola_modelo', auto_ack=False)
            if metodo is not None:
                break
            time.sleep(0.3)

        if metodo is None:
            raise TimeoutError(
                "No llego ningun modelo a cola_modelo dentro del tiempo de "
                "espera. Verifica que el Productor ya haya publicado uno."
            )

        modelo_pb = SerializadorProtobuf.deserializar(cuerpo, pb2.ModeloFutbol)
        canal.basic_nack(delivery_tag=metodo.delivery_tag, requeue=True)

        self.formula_evaluacion = modelo_pb.formula_evaluacion
        if self.formula_evaluacion not in REGISTRO_EVALUADORES:
            raise ValueError(
                f"No hay funcion de evaluacion registrada para "
                f"'{self.formula_evaluacion}'. Revisa evaluadores.py o "
                f"si Productor.py cambio el nombre de formula_evaluacion."
            )
        print(
            f"[{self.id_consumidor}] Modelo cargado: id={modelo_pb.id_modelo} "
            f"formula={self.formula_evaluacion} "
            f"variables={[v.nombre for v in modelo_pb.variables]}"
        )

    
    # obtener escenario + ejecutar el modelo
    def procesar_escenario(self, cuerpo_bytes: bytes) -> "pb2.ResultadoPartido":
        escenario_pb = SerializadorProtobuf.deserializar(cuerpo_bytes, pb2.EscenarioPartido)

        funcion_evaluar = REGISTRO_EVALUADORES[self.formula_evaluacion]
        gana_local, goles_local, goles_visitante = funcion_evaluar(escenario_pb)

        return pb2.ResultadoPartido(
            id_escenario=escenario_pb.id_escenario,
            gana_local=gana_local,
            goles_local=goles_local,
            goles_visitante=goles_visitante,
        )

    # Paso 4: publicar resultado
    def publicar_resultado(self, resultado_pb: "pb2.ResultadoPartido"):
        self.conector.publicar_en_cola(
            'cola_resultados', SerializadorProtobuf.serializar(resultado_pb)
        )
    
    # Ipublicacion de estadisticas propias
    def publicar_estadisticas(self):
        ahora = time.time()
        transcurrido = ahora - self._inicio_ventana
        tasa_por_segundo = self._procesados_ventana / transcurrido if transcurrido > 0 else 0.0
        prob_local_acumulada = (
            self.victorias_local / self.escenarios_procesados
            if self.escenarios_procesados else 0.0
        )

        evento = pb2.EventoEstadistica(
            origen=self.id_consumidor,
            tasa_por_segundo=tasa_por_segundo,
            probabilidad_victoria_local_acumulada=prob_local_acumulada,
            escenarios_procesados=self.escenarios_procesados,
        )
        self.conector.publicar_en_exchange(
            'exchange_estadisticas', SerializadorProtobuf.serializar(evento)
        )

        self._inicio_ventana = ahora
        self._procesados_ventana = 0


    def ejecutar(self, intervalo_estadisticas=2.0):
        self.cargar_modelo()

        ultimo_reporte = time.time()

        def _callback(canal, metodo, _propiedades, cuerpo):
            nonlocal ultimo_reporte

            resultado_pb = self.procesar_escenario(cuerpo)
            self.publicar_resultado(resultado_pb)

            self.escenarios_procesados += 1
            self._procesados_ventana += 1
            if resultado_pb.gana_local:
                self.victorias_local += 1

            # ACK solo despues de publicar el resultado: si este proceso
            # muere a medio camino, RabbitMQ reencola el escenario y otro
            # Consumidor lo vuelve a tomar, sin duplicados confirmados.
            canal.basic_ack(delivery_tag=metodo.delivery_tag)

            if time.time() - ultimo_reporte >= intervalo_estadisticas:
                self.publicar_estadisticas()
                ultimo_reporte = time.time()

            if self.escenarios_procesados % 50 == 0:
                print(
                    f"[{self.id_consumidor}] procesados={self.escenarios_procesados} "
                    f"prob_local={self.victorias_local / self.escenarios_procesados:.3f}"
                )

        print(f"[{self.id_consumidor}] Escuchando cola_escenarios (prefetch_count=1)...")
        self.conector.consumir('cola_escenarios', _callback, auto_ack=False, prefetch=1)
        self.conector.iniciar_consumo()


def ejecutar_consumidor_distribuido():
    parser = argparse.ArgumentParser(description="Consumidor de la simulacion Montecarlo")
    parser.add_argument(
        '--id',
        default=os.getenv('CONSUMIDOR_ID', 'consumidor-1'),
        help=(
            "Identificador de esta instancia. El Dashboard busca las "
            "subcadenas 'consumidor-1'..'consumidor-4' en este valor "
            "para graficar throughput por componente; usalas tal cual."
        ),
    )
    args = parser.parse_args()

    print(f" Consumidor '{args.id}': inicializando nodo evaluador...")

    try:
        conector = ConectorRabbitMQ()
        print("Conexion establecida con RabbitMQ con exito.")
    except Exception as e:
        print(f" Error critico al conectar a RabbitMQ: {e}")
        print("Revisa que el contenedor Docker este encendido y el .env configurado.")
        return

    consumidor = Consumidor(conector, args.id)
    try:
        consumidor.ejecutar()
    except KeyboardInterrupt:
        print(f"\n[{args.id}] Interrumpido por el usuario, cerrando conexion...")
    except TimeoutError as e:
        print(f"[{args.id}] {e}")
    finally:
        conector.cerrar()
        print("Conexion con RabbitMQ liberada de forma segura.")


if __name__ == "__main__":
    ejecutar_consumidor_distribuido()

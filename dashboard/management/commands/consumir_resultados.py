# dashboard/management/commands/consumir_resultados.py
from django.core.management.base import BaseCommand
from django.core.cache import cache

from common.middleware import ConectorRabbitMQ, SerializadorProtobuf
from common.futbol_mensajes_pb2 import ResultadoPartido

class Command(BaseCommand):
    help = "Consume los marcadores de los partidos desde RabbitMQ para el Dashboard"

    def handle(self, *args, **kwargs):
        rabbit = ConectorRabbitMQ()

        self.stdout.write(self.style.SUCCESS("Dashboard escuchando marcadores en 'cola_resultados'..."))

        def callback(ch, method, properties, body):
            # 1. Deserializar el mensaje
            resultado = SerializadorProtobuf.deserializar(body, ResultadoPartido)

            # 2. Traer el pizarrón de datos actual (Caché)
            data = cache.get("dashboard_data", {
                "partidos": 0,
                "victorias_local": 0,
                "probabilidad": 0,
                "throughput": 0,
                "convergencia": [],
                "throughput_componentes": [0, 0, 0, 0],
                "distribucion": [0, 0, 0], # [Victorias Local, Victorias Visita, Empates]
                "ultimos_resultados": []
            })

            # 3. Lógica para la Gráfica de Pastel (Distribución)
            if resultado.goles_local > resultado.goles_visitante:
                data["distribucion"][0] += 1
                data["victorias_local"] += 1
            elif resultado.goles_visitante > resultado.goles_local:
                data["distribucion"][1] += 1
            else:
                data["distribucion"][2] += 1

            # 4. Lógica para la Tabla de Últimos Resultados
            nuevo_resultado = {
                "id": f"#{resultado.id_escenario[:4]}",
                "marcador": f"{resultado.goles_local}-{resultado.goles_visitante}",
                "tipo": "Local" if resultado.goles_local > resultado.goles_visitante else ("Visitante" if resultado.goles_visitante > resultado.goles_local else "Empate")
            }
            
            # Validación de seguridad por si el otro proceso creó la caché primero
            if "ultimos_resultados" not in data:
                data["ultimos_resultados"] = []
                
            # Agregamos al inicio de la lista y mantenemos solo los últimos 5
            data["ultimos_resultados"].insert(0, nuevo_resultado)
            data["ultimos_resultados"] = data["ultimos_resultados"][:5]

            # 5. Guardar de nuevo en caché
            cache.set("dashboard_data", data, timeout=None)
            
            # Imprimir en consola para validación visual
            print(f"[Marcador] {nuevo_resultado['id']} | {nuevo_resultado['marcador']} ({nuevo_resultado['tipo']})")

            # 6. Confirmar que leímos el mensaje (Para que RabbitMQ lo borre de la cola)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        # Configurar y arrancar el consumidor
        rabbit.consumir(
            nombre_cola='cola_resultados',
            callback=callback,
            auto_ack=False
        )
        rabbit.iniciar_consumo()
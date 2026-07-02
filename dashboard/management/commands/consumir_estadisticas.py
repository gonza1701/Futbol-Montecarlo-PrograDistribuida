from django.core.management.base import BaseCommand
from django.core.cache import cache

from common.middleware import ConectorRabbitMQ, SerializadorProtobuf
from common.futbol_mensajes_pb2 import EventoEstadistica


class Command(BaseCommand):
    help = "Consume estadísticas desde RabbitMQ para el Dashboard"

    def handle(self, *args, **kwargs):
        rabbit = ConectorRabbitMQ()

        # Crear cola temporal exclusiva para este dashboard
        resultado = rabbit.canal.queue_declare(queue='', exclusive=True)
        cola_dashboard = resultado.method.queue

        # Enlazar la cola temporal al exchange fanout
        rabbit.canal.queue_bind(
            exchange='exchange_estadisticas',
            queue=cola_dashboard
        )

        self.stdout.write(self.style.SUCCESS(
            f"Dashboard escuchando estadísticas en {cola_dashboard}"
        ))

        def callback(ch, method, properties, body):
            evento = SerializadorProtobuf.deserializar(
                body,
                EventoEstadistica
            )

            data = cache.get("dashboard_data", {
                "partidos": 0,
                "victorias_local": 0,
                "probabilidad": 0,
                "throughput": 0,
                "convergencia": [],
                "throughput_componentes": [0, 0, 0, 0],
                "distribucion": [0, 0, 0]
            })

            data["partidos"] = evento.escenarios_procesados
            data["probabilidad"] = round(
                evento.probabilidad_victoria_local_acumulada,
                2
            )
            data["throughput"] = round(evento.tasa_por_segundo, 2)

            data["convergencia"].append(data["probabilidad"])
            data["convergencia"] = data["convergencia"][-30:]

            origen = evento.origen

            if "consumidor-1" in origen:
                data["throughput_componentes"][0] = data["throughput"]
            elif "consumidor-2" in origen:
                data["throughput_componentes"][1] = data["throughput"]
            elif "consumidor-3" in origen:
                data["throughput_componentes"][2] = data["throughput"]
            elif "consumidor-4" in origen:
                data["throughput_componentes"][3] = data["throughput"]

            cache.set("dashboard_data", data, timeout=None)

            print(
                f"[Dashboard] {evento.origen} | "
                f"{evento.escenarios_procesados} escenarios | "
                f"{evento.tasa_por_segundo} msg/s | "
                f"{evento.probabilidad_victoria_local_acumulada}%"
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)

        rabbit.consumir(
            nombre_cola=cola_dashboard,
            callback=callback,
            auto_ack=False
        )

        rabbit.iniciar_consumo()
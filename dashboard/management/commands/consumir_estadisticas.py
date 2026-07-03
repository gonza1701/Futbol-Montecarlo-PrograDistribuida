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
            evento = SerializadorProtobuf.deserializar(body, EventoEstadistica)

            
            data = cache.get("dashboard_data", {
                "partidos": 0,
                "victorias_local": 0,
                "throughput": 0,
                "throughput_componentes": [0, 0, 0, 0],
                "distribucion": [0, 0, 0],
                "convergencia_local": [],
                "convergencia_visita": [],
                "convergencia_empate": [],
                "ultimos_resultados": [],
            })
            data.setdefault("throughput", 0)
            data.setdefault("throughput_componentes", [0, 0, 0, 0])

           
            data["throughput"] = round(evento.tasa_por_segundo, 2)

            origen = evento.origen
            if "consumidor-1" in origen:
                data["throughput_componentes"][0] = round(evento.tasa_por_segundo, 2)
            elif "consumidor-2" in origen:
                data["throughput_componentes"][1] = round(evento.tasa_por_segundo, 2)
            elif "consumidor-3" in origen:
                data["throughput_componentes"][2] = round(evento.tasa_por_segundo, 2)
            elif "consumidor-4" in origen:
                data["throughput_componentes"][3] = round(evento.tasa_por_segundo, 2)

            cache.set("dashboard_data", data, timeout=None)

            print(
                f"[Dashboard] {evento.origen} | "
                f"{evento.escenarios_procesados} escenarios | "
                f"{evento.tasa_por_segundo} msg/s"
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)

        rabbit.consumir(
            nombre_cola=cola_dashboard,
            callback=callback,
            auto_ack=False
        )

        rabbit.iniciar_consumo()
# dashboard/management/commands/consumir_resultados.py

from django.core.management.base import BaseCommand
from django.core.cache import cache

from common.middleware import ConectorRabbitMQ, SerializadorProtobuf
from common.futbol_mensajes_pb2 import ResultadoPartido


class Command(BaseCommand):
    help = "Consume los marcadores de los partidos desde RabbitMQ para el Dashboard"

    def handle(self, *args, **kwargs):
        rabbit = ConectorRabbitMQ()

        self.stdout.write(
            self.style.SUCCESS(
                "Dashboard escuchando marcadores en 'cola_resultados'..."
            )
        )

        def callback(ch, method, properties, body):
            # 1. Deserializar el mensaje
            resultado = SerializadorProtobuf.deserializar(body, ResultadoPartido)

            # 2. Recuperar o inicializar datos del dashboard
            data = cache.get(
                "dashboard_data",
                {
                    "partidos": 0,
                    "victorias_local": 0,
                    "probabilidad": 0,
                    "throughput": 0,
                    "throughput_componentes": [0, 0, 0, 0],
                    "distribucion": [0, 0, 0],  # [Local, Visita, Empate]
                    "convergencia_local": [],
                    "convergencia_visita": [],
                    "convergencia_empate": [],
                    "ultimos_resultados": [],
                },
            )

            # Compatibilidad con cachés antiguas
            data.setdefault("distribucion", [0, 0, 0])
            data.setdefault("convergencia_local", [])
            data.setdefault("convergencia_visita", [])
            data.setdefault("convergencia_empate", [])
            data.setdefault("ultimos_resultados", [])

            # 3. Actualizar conteos
            if resultado.goles_local > resultado.goles_visitante:
                data["distribucion"][0] += 1
                data["victorias_local"] += 1

            elif resultado.goles_visitante > resultado.goles_local:
                data["distribucion"][1] += 1

            else:
                data["distribucion"][2] += 1

            # El total de partidos siempre coincide con la suma de las tres categorías
            data["partidos"] = sum(data["distribucion"])

            # 4. Calcular convergencia histórica
            total = data["partidos"]

            if total > 0:
                porcentaje_local = (
                    data["distribucion"][0] / total
                ) * 100

                porcentaje_visita = (
                    data["distribucion"][1] / total
                ) * 100

                porcentaje_empate = (
                    data["distribucion"][2] / total
                ) * 100

                historiales = [
                    ("convergencia_local", porcentaje_local),
                    ("convergencia_visita", porcentaje_visita),
                    ("convergencia_empate", porcentaje_empate),
                ]

                for llave, valor in historiales:
                    data[llave].append(valor)

                    # Mantener únicamente los últimos 30 puntos
                    if len(data[llave]) > 30:
                        data[llave].pop(0)

            # 5. Tabla de últimos resultados
            nuevo_resultado = {
                "id": f"#{resultado.id_escenario[:4]}",
                "marcador": f"{resultado.goles_local}-{resultado.goles_visitante}",
                "tipo": (
                    "Local"
                    if resultado.goles_local > resultado.goles_visitante
                    else (
                        "Visitante"
                        if resultado.goles_visitante > resultado.goles_local
                        else "Empate"
                    )
                ),
            }

            # Agregar al inicio y conservar únicamente los últimos 5
            data["ultimos_resultados"].insert(0, nuevo_resultado)
            data["ultimos_resultados"] = data["ultimos_resultados"][:5]

            # 6. Guardar nuevamente en caché
            cache.set("dashboard_data", data, timeout=None)

            # Validación visual en consola
            print(
                f"[Marcador] {nuevo_resultado['id']} | "
                f"{nuevo_resultado['marcador']} "
                f"({nuevo_resultado['tipo']})"
            )

            # 7. Confirmar recepción del mensaje
            ch.basic_ack(delivery_tag=method.delivery_tag)

        # Configurar consumidor
        rabbit.consumir(
            nombre_cola="cola_resultados",
            callback=callback,
            auto_ack=False,
        )

        rabbit.iniciar_consumo()
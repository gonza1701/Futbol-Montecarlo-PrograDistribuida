# common/middleware.py
import os
import pika
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

class SerializadorProtobuf:
    """
    Encapsula la serialización/deserialización aislando la dependencia de Protobuf 
    del resto del código.
    """
    @staticmethod
    def serializar(mensaje_proto):
        # Convierte el objeto Python a bytes puros
        return mensaje_proto.SerializeToString()

    @staticmethod
    def deserializar(bytes_mensaje, clase_proto):
        # Toma los bytes y los reconstruye en la clase Protobuf especificada
        mensaje = clase_proto()
        mensaje.ParseFromString(bytes_mensaje)
        return mensaje


class ConectorRabbitMQ:
    """
    Encapsula la conexión al bróker, declaración de topología y los métodos 
    publicar() y consumir().
    """
    def __init__(self):
        host = os.getenv('RABBITMQ_HOST', 'localhost')
        port = int(os.getenv('RABBITMQ_PORT', 5672))
        usuario = os.getenv('RABBITMQ_USER', 'guest')
        password = os.getenv('RABBITMQ_PASS', 'guest')
        # Configuración de credenciales y conexión a la infraestructura de mensajería
        credenciales = pika.PlainCredentials(usuario, password)
        parametros = pika.ConnectionParameters(host=host, port=port, credentials=credenciales)
        self.conexion = pika.BlockingConnection(parametros)
        self.canal = self.conexion.channel()
        
        # Al instanciar, garantizamos que las colas y exchanges existen
        self._declarar_topologia()

    def _declarar_topologia(self):
        # 1. Cola de modelo con política de expiración (TTL)
        # Si un modelo no se lee en 60s, caduca para evitar modelos obsoletos
        self.canal.queue_declare(
            queue='cola_modelo', 
            durable=True, 
            arguments={'x-message-ttl': 60000}
        )
        
        # 2. Colas de trabajo (Work Queues) para escenarios y resultados
        self.canal.queue_declare(queue='cola_escenarios', durable=True)
        self.canal.queue_declare(queue='cola_resultados', durable=True)
        
        # 3. Exchange tipo fanout para la difusión (broadcast) de métricas
        self.canal.exchange_declare(exchange='exchange_estadisticas', exchange_type='fanout')
        print("[Middleware] Topología de RabbitMQ declarada correctamente.")

    def publicar_en_cola(self, nombre_cola, bytes_mensaje):
        """Publica un mensaje persistente en una cola específica."""
        self.canal.basic_publish(
            exchange='',
            routing_key=nombre_cola,
            body=bytes_mensaje,
            properties=pika.BasicProperties(
                delivery_mode=2  # Hace que el mensaje sea persistente en el disco del bróker
            )
        )

    def publicar_en_exchange(self, nombre_exchange, bytes_mensaje):
        """Publica un mensaje en un exchange para difusión."""
        self.canal.basic_publish(
            exchange=nombre_exchange,
            routing_key='',
            body=bytes_mensaje
        )

    def consumir(self, nombre_cola, callback, auto_ack=False, prefetch=None):
        """Prepara el canal para consumir mensajes de una cola."""
        if prefetch is not None:
            # prefetch_count=1 asegura el balanceo de carga justo entre Consumidores
            self.canal.basic_qos(prefetch_count=prefetch)
            
        self.canal.basic_consume(
            queue=nombre_cola, 
            on_message_callback=callback, 
            auto_ack=auto_ack
        )

    def purgar_cola(self, nombre_cola):
        """Limpia todos los mensajes de una cola (útil al cargar un nuevo modelo)."""
        self.canal.queue_purge(queue=nombre_cola)

    def iniciar_consumo(self):
        """Inicia el bucle bloqueante para escuchar mensajes."""
        self.canal.start_consuming()

    def cerrar(self):
        """Cierra la conexión de forma segura."""
        if self.conexion and self.conexion.is_open:
            self.conexion.close()
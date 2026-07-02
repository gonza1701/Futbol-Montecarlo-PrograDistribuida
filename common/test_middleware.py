# common/test_middleware.py
import sys
import futbol_mensajes_pb2
from middleware import ConectorRabbitMQ, SerializadorProtobuf

def test_middleware():
    print(" INICIANDO PRUEBA AISLADA DEL MIDDLEWARE ")

    # 1. Iniciar conexión
    try:
        conector = ConectorRabbitMQ(host='localhost')
    except Exception as e:
        print(f"[-] Error al conectar con RabbitMQ. Detalles: {e}")
        sys.exit(1)

    # 2. Crear un mensaje Protobuf de prueba (ResultadoPartido)
    mensaje_prueba = futbol_mensajes_pb2.ResultadoPartido(
        id_escenario="TEST-UUID-9999",
        gana_local=True,
        goles_local=3,
        goles_visitante=1
    )
    print(f"\n[1] Mensaje Protobuf original creado:\nID: {mensaje_prueba.id_escenario} | Marcador: {mensaje_prueba.goles_local}-{mensaje_prueba.goles_visitante}")

    # 3. Serializar el mensaje a bytes puros usando la librería
    bytes_mensaje = SerializadorProtobuf.serializar(mensaje_prueba)
    print(f"[2] Mensaje serializado a bytes: {bytes_mensaje}")

    # 4. Publicar el mensaje en la cola de resultados
    conector.publicar_en_cola('cola_resultados', bytes_mensaje)
    print("[3] Mensaje publicado exitosamente en 'cola_resultados'.")

    # 5. Definir la función Callback que se ejecutará al recibir el mensaje
    def callback_prueba(canal, metodo, propiedades, cuerpo_mensaje):
        print("\n[4] Mensaje recibido desde RabbitMQ")
        
        # Deserializar los bytes de vuelta a un objeto Python
        mensaje_recibido = SerializadorProtobuf.deserializar(cuerpo_mensaje, futbol_mensajes_pb2.ResultadoPartido)
        
        print(f"[5] Mensaje deserializado:")
        print(f"    - Escenario: {mensaje_recibido.id_escenario}")
        print(f"    - Gana Local: {mensaje_recibido.gana_local}")
        print(f"    - Goles Local: {mensaje_recibido.goles_local}")
        print(f"    - Goles Visita: {mensaje_recibido.goles_visitante}")
        
        # Confirmar al bróker que procesamos el mensaje (ACK) y cerrar la conexión
        canal.basic_ack(delivery_tag=metodo.delivery_tag)
        print("\n[+] Prueba superada. Cerrando conexión...")
        conector.cerrar()

    # 6. Preparar al consumidor y arrancar el bucle
    print("\n[*] Preparando consumidor. Escuchando 'cola_resultados'...")
    conector.consumir('cola_resultados', callback_prueba, auto_ack=False)
    
    conector.iniciar_consumo()

if __name__ == '__main__':
    test_middleware()
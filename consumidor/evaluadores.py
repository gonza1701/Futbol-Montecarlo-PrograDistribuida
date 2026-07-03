import random

# Minutos reglamentarios de un partido.
MINUTOS_PARTIDO = 90

# Epsilon para evitar division por cero si algun muestreo de la
# exponencial (t_gol_local / t_gol_visitante) da un valor extremadamente
# cercano a 0.
_EPS = 1e-9


def simular_proceso_poisson(tasa_por_minuto, minutos=MINUTOS_PARTIDO):
    if tasa_por_minuto <= 0:
        return 0

    tiempo_transcurrido = 0.0
    goles = 0
    while True:
        tiempo_transcurrido += random.expovariate(tasa_por_minuto)
        if tiempo_transcurrido > minutos:
            break
        goles += 1
    return goles


def evaluar_montecarlo_basico(escenario_pb):
    # Asumimos que t_gol es la expectativa de goles por partido (ej. 1.5)
    expectativa_local = max(escenario_pb.t_gol_local, _EPS)
    expectativa_visitante = max(escenario_pb.t_gol_visitante, _EPS)
    
    rendimiento_local = max(escenario_pb.rendimiento_local, 0.0)
    rendimiento_visitante = max(escenario_pb.rendimiento_visitante, 0.0)
    factor_var = escenario_pb.factor_var  # acotado en [-1, 1]

    # Convertimos la expectativa del partido entero a una tasa por minuto
    tasa_local = (expectativa_local / MINUTOS_PARTIDO) * (rendimiento_local / 70) * (1 + 0.05 * factor_var)
    tasa_visitante = (expectativa_visitante / MINUTOS_PARTIDO) * (rendimiento_visitante / 70) * (1 - 0.05 * factor_var)

    goles_local = simular_proceso_poisson(tasa_local, MINUTOS_PARTIDO)
    goles_visitante = simular_proceso_poisson(tasa_visitante, MINUTOS_PARTIDO)

    gana_local = goles_local > goles_visitante
    return gana_local, goles_local, goles_visitante


REGISTRO_EVALUADORES = {
    "evaluacion_montecarlo_basica": evaluar_montecarlo_basico,
}

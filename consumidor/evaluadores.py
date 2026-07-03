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
    t_gol_local = max(escenario_pb.t_gol_local, _EPS)
    t_gol_visitante = max(escenario_pb.t_gol_visitante, _EPS)
    # El rendimiento es un porcentaje animico/fisico; se acota a >= 0
    # por si la Normal(70,10) muestrea un valor extremo poco realista.
    rendimiento_local = max(escenario_pb.rendimiento_local, 0.0)
    rendimiento_visitante = max(escenario_pb.rendimiento_visitante, 0.0)
    factor_var = escenario_pb.factor_var  #acotado en [-1, 1]

    tasa_local = (1 / t_gol_local) * (rendimiento_local / 70) * (1 + 0.05 * factor_var)
    tasa_visitante = (1 / t_gol_visitante) * (rendimiento_visitante / 70) * (1 - 0.05 * factor_var)

    goles_local = simular_proceso_poisson(tasa_local, MINUTOS_PARTIDO)
    goles_visitante = simular_proceso_poisson(tasa_visitante, MINUTOS_PARTIDO)

    gana_local = goles_local > goles_visitante
    return gana_local, goles_local, goles_visitante


REGISTRO_EVALUADORES = {
    "evaluacion_montecarlo_basica": evaluar_montecarlo_basico,
}

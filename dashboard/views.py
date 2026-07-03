from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache


def dashboard(request):
    return render(request, "dashboard/index.html")


def dashboard_api(request):
    data = cache.get(
        "dashboard_data",
        {
            "partidos": 0,
            "victorias_local": 0,
            "throughput": 0,
            "throughput_componentes": [0, 0, 0, 0],
            "distribucion": [0, 0, 0],
            "convergencia_local": [],
            "convergencia_visita": [],
            "convergencia_empate": [],
            "ultimos_resultados": [],
        },
    )

    # Crear la lista de consumidores a partir del throughput
    throughput = data.get("throughput_componentes", [0, 0, 0, 0])

    data["consumidores"] = [
        {
            "nombre": "consumidor-1",
            "procesados": throughput[0],
        },
        {
            "nombre": "consumidor-2",
            "procesados": throughput[1],
        },
        {
            "nombre": "consumidor-3",
            "procesados": throughput[2],
        },
        {
            "nombre": "consumidor-4",
            "procesados": throughput[3],
        },
    ]

    return JsonResponse(data)
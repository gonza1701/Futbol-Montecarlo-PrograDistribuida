from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache


def dashboard(request):
    return render(request, 'dashboard/index.html')


def dashboard_api(request):
    data = cache.get("dashboard_data", {
        "partidos": 0,
        "victorias_local": 0,
        "throughput": 0,
        "throughput_componentes": [0, 0, 0, 0],
        "distribucion": [0, 0, 0],
        "convergencia_local": [],
        "convergencia_visita": [],
        "convergencia_empate": [],
        "ultimos_resultados": []
    })
    return JsonResponse(data)
from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache


def dashboard(request):
    return render(request, 'dashboard/index.html')


def dashboard_api(request):
    data = cache.get("dashboard_data", {
        "partidos": 0,
        "victorias_local": 0,
        "probabilidad": 0,
        "throughput": 0,
        "convergencia": [],
        "throughput_componentes": [0, 0, 0, 0],
        "distribucion": [0, 0, 0]
    })

    return JsonResponse(data)
// ========================================
// DASHBOARD MONTE CARLO - GRÁFICAS
// ========================================

document.addEventListener('DOMContentLoaded', function () {

    // ---------- GRÁFICA DE CONVERGENCIA ----------
    const ctxConv = document.getElementById('convergenciaChart').getContext('2d');

    const gradienteConvergencia = ctxConv.createLinearGradient(0, 0, 0, 150);
    gradienteConvergencia.addColorStop(0, 'rgba(66, 165, 245, 0.25)');
    gradienteConvergencia.addColorStop(1, 'rgba(66, 165, 245, 0.01)');

    const convergenciaChart = new Chart(ctxConv, {
        type: 'line',
        data: {
            labels: Array.from({ length: 30 }, (_, i) => i + 1),
            datasets: [{
                label: 'Probabilidad local',
                data: [62, 64, 63, 65, 67, 66, 68, 67, 69, 70, 68, 71, 72, 70, 73, 74, 72, 75, 76, 74, 77, 78, 76, 79, 80, 78, 81, 82, 80, 83],
                borderColor: '#42a5f5',
                backgroundColor: gradienteConvergencia,
                borderWidth: 2.5,
                pointBackgroundColor: '#42a5f5',
                pointBorderColor: '#0b1a24',
                pointBorderWidth: 1.5,
                pointRadius: 3,
                tension: 0.2,
                fill: true,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0d1a22',
                    titleColor: '#b0d0e0',
                    bodyColor: '#dce8ef',
                    borderColor: '#2a4a5a',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            return `Prob: ${context.parsed.y}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(40, 70, 85, 0.2)', drawBorder: false },
                    ticks: { color: '#5a7a8a', font: { size: 9 } }
                },
                y: {
                    grid: { color: 'rgba(40, 70, 85, 0.2)', drawBorder: false },
                    ticks: { color: '#5a7a8a', font: { size: 9 }, callback: value => value + '%' },
                    min: 55,
                    max: 88
                }
            },
            interaction: {
                intersect: false,
                mode: 'index',
            }
        }
    });

    // ---------- GRÁFICA DE THROUGHPUT ----------
    const ctxThrough = document.getElementById('throughputChart').getContext('2d');

    const throughputChart = new Chart(ctxThrough, {
        type: 'bar',
        data: {
            labels: ['API', 'Simulador', 'Cola', 'Procesador'],
            datasets: [{
                label: 'Throughput (msg/s)',
                data: [320, 480, 255, 410],
                backgroundColor: [
                    'rgba(1, 251, 255, 0.3)',
                    'rgba(0, 248, 12, 0.4)',
                    'rgba(255, 191, 0, 0.36)',
                    'rgba(255, 11, 6, 0.29)'
                ],
                borderColor: [
                    'rgb(1, 251, 255)',
                    'rgb(0, 248, 12)',
                    'rgb(255, 191, 0)',
                    'rgb(255, 11, 6)'
                ],
                borderWidth: 1.8,
                borderRadius: 6,
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0d1a22',
                    titleColor: '#b0d0e0',
                    bodyColor: '#dce8ef',
                    borderColor: '#2a4a5a',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.x} msg/s`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(40, 70, 85, 0.15)', drawBorder: false },
                    ticks: { color: '#5a7a8a', font: { size: 9 } },
                    max: 600,
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#8aaabc', font: { size: 10, weight: '500' } }
                }
            }
        }
    });

    // ---------- GRÁFICA DE PASTEL ----------
    const ctxPie = document.getElementById('pieChart').getContext('2d');

    const pieChart = new Chart(ctxPie, {
        type: 'pie',
        data: {
            labels: ['Local', 'Visitante', 'Empate'],
            datasets: [{
                data: [58, 25, 17],
                backgroundColor: [
                    'rgba(0, 248, 12, 0.61)',
                    'rgba(255, 10, 6, 0.57)',
                    'rgba(1, 251, 255, 0.63)'
                    
                ],
                borderColor: [
                    'rgb(0, 248, 12)',
                    'rgb(255, 11, 6)',
                    'rgb(1, 251, 255)'
                    
                ],
                borderWidth: 2,
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: 'rgba(200, 230, 255, 0.8)',
                        font: {
                            size: 10,
                            weight: '500'
                        },
                        padding: 10,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        boxWidth: 10,
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(10, 10, 20, 0.95)',
                    titleColor: '#b0d0e0',
                    bodyColor: '#dce8ef',
                    borderColor: 'rgba(0, 255, 200, 0.3)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 10,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${percentage}%`;
                        }
                    }
                }
            },
            cutout: '0%',
            animation: {
                animateRotate: true,
                duration: 1200
            }
        }
    });

    async function cargarDatosDashboard() {
        try {
            const response = await fetch('/api/dashboard/');
            const data = await response.json();

            document.getElementById('partidos').innerText =
                data.partidos.toLocaleString();

            document.getElementById('victorias').innerText =
                data.victorias_local.toLocaleString();

            document.getElementById('probabilidad').innerHTML =
                `${data.probabilidad}<small>%</small>`;

            document.getElementById('throughput').innerHTML =
                `${data.throughput}<small>/s</small>`;

            convergenciaChart.data.labels =
                data.convergencia.map((_, i) => i + 1);

            convergenciaChart.data.datasets[0].data =
                data.convergencia;

            convergenciaChart.update();

            throughputChart.data.datasets[0].data =
                data.throughput_componentes;

            throughputChart.update();

            pieChart.data.datasets[0].data =
                data.distribucion;

            pieChart.update();

        } catch (error) {
            console.error('Error cargando datos del dashboard:', error);
        }
    }

    cargarDatosDashboard();
    setInterval(cargarDatosDashboard, 1000);

    console.log('✅ Dashboard Montecarlo · gráficas cargadas');
});
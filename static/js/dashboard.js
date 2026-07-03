// ========================================
// DASHBOARD MONTE CARLO - GRÁFICAS
// ========================================

document.addEventListener("DOMContentLoaded", function () {
  // ---------- GRÁFICA DE CONVERGENCIA ----------
  const ctxConv = document.getElementById("convergenciaChart").getContext("2d");

  const convergenciaChart = new Chart(ctxConv, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Local",
          data: [],
          borderColor: "#00f80c",
          tension: 0.3,
          pointRadius: 0,
        },
        {
          label: "Visitante",
          data: [],
          borderColor: "#ff0b06",
          tension: 0.3,
          pointRadius: 0,
        },
        {
          label: "Empate",
          data: [],
          borderColor: "#01fbff",
          tension: 0.3,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true, labels: { color: "#8aaabc" } },
        tooltip: {
          backgroundColor: "#0d1a22",
          titleColor: "#b0d0e0",
          bodyColor: "#dce8ef",
          borderColor: "#2a4a5a",
          borderWidth: 1,
          cornerRadius: 8,
          callbacks: {
            label: (context) =>
              `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: "rgba(40, 70, 85, 0.2)", drawBorder: false },
          ticks: { color: "#5a7a8a", font: { size: 9 } },
        },
        y: {
          grid: { color: "rgba(40, 70, 85, 0.2)", drawBorder: false },
          ticks: {
            color: "#5a7a8a",
            font: { size: 9 },
            callback: (value) => value + "%",
          },
          min: 0,
          max: 100,
        },
      },
      interaction: { intersect: false, mode: "index" },
    },
  });

  // ---------- GRÁFICA DE THROUGHPUT ----------
  const ctxThrough = document
    .getElementById("throughputChart")
    .getContext("2d");

  const throughputChart = new Chart(ctxThrough, {
    type: "bar",
    data: {
      labels: ["Consumidor 1", "Consumidor 2", "Consumidor 3", "Consumidor 4"],
      datasets: [
        {
          label: "Throughput (esc/s)",
          data: [0, 0, 0, 0],
          backgroundColor: [
            "rgba(1, 251, 255, 0.3)",
            "rgba(0, 248, 12, 0.4)",
            "rgba(255, 191, 0, 0.36)",
            "rgba(255, 11, 6, 0.29)",
          ],
          borderColor: [
            "rgb(1, 251, 255)",
            "rgb(0, 248, 12)",
            "rgb(255, 191, 0)",
            "rgb(255, 11, 6)",
          ],
          borderWidth: 1.8,
          borderRadius: 6,
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#0d1a22",
          titleColor: "#b0d0e0",
          bodyColor: "#dce8ef",
          borderColor: "#2a4a5a",
          borderWidth: 1,
          cornerRadius: 8,
          callbacks: { label: (context) => `${context.parsed.x} esc/s` },
        },
      },
      scales: {
        x: {
          grid: { color: "rgba(40, 70, 85, 0.15)", drawBorder: false },
          ticks: { color: "#5a7a8a", font: { size: 9 } },
          beginAtZero: true,
        },
        y: {
          grid: { display: false },
          ticks: { color: "#8aaabc", font: { size: 10, weight: "500" } },
        },
      },
    },
  });

  // ---------- GRÁFICA DE PASTEL ----------
  const ctxPie = document.getElementById("pieChart").getContext("2d");

  const pieChart = new Chart(ctxPie, {
    type: "pie",
    data: {
      labels: ["Local", "Visitante", "Empate"],
      datasets: [
        {
          data: [0, 0, 0],
          backgroundColor: [
            "rgba(0, 248, 12, 0.61)",
            "rgba(255, 10, 6, 0.57)",
            "rgba(1, 251, 255, 0.63)",
          ],
          borderColor: [
            "rgb(0, 248, 12)",
            "rgb(255, 11, 6)",
            "rgb(1, 251, 255)",
          ],
          borderWidth: 2,
          hoverOffset: 8,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: "rgba(200, 230, 255, 0.8)",
            font: { size: 10, weight: "500" },
            padding: 10,
            usePointStyle: true,
            pointStyle: "circle",
            boxWidth: 10,
          },
        },
        tooltip: {
          backgroundColor: "rgba(10, 10, 20, 0.95)",
          titleColor: "#b0d0e0",
          bodyColor: "#dce8ef",
          borderColor: "rgba(0, 255, 200, 0.3)",
          borderWidth: 1,
          cornerRadius: 8,
          padding: 10,
          callbacks: {
            label: function (context) {
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage =
                total > 0 ? ((context.parsed / total) * 100).toFixed(1) : "0.0";
              return `${context.label}: ${percentage}%`;
            },
          },
        },
      },
      cutout: "0%",
      animation: { animateRotate: true, duration: 1200 },
    },
  });

  async function cargarDatosDashboard() {
    try {
      const response = await fetch("/api/dashboard/");
      const data = await response.json();

      const partidos = data.partidos || 0;
      const distribucion = data.distribucion || [0, 0, 0];
      const convLocal = data.convergencia_local || [];
      const convVisita = data.convergencia_visita || [];
      const convEmpate = data.convergencia_empate || [];
      const throughputComponentes = data.throughput_componentes || [0, 0, 0, 0];

      // --- KPIs ---
      document.getElementById("partidos").innerText = partidos.toLocaleString();
      document.getElementById("victorias").innerText = (
        data.victorias_local || 0
      ).toLocaleString();
      document.getElementById("throughput").innerHTML =
        `${data.throughput || 0}<small>/s</small>`;

      // Pronóstico real: se deriva directamente de distribucion/partidos,
      const probLocal = partidos > 0 ? (distribucion[0] / partidos) * 100 : 0;
      const probVisita = partidos > 0 ? (distribucion[1] / partidos) * 100 : 0;
      const probEmpate = partidos > 0 ? (distribucion[2] / partidos) * 100 : 0;
      document.getElementById("prob_local").innerText = probLocal.toFixed(1);
      document.getElementById("prob_visita").innerText = probVisita.toFixed(1);
      document.getElementById("prob_empate").innerText = probEmpate.toFixed(1);

      // --- Gráfica de convergencia ---
      const maxPuntos = Math.max(
        convLocal.length,
        convVisita.length,
        convEmpate.length,
      );
      convergenciaChart.data.labels = Array.from(
        { length: maxPuntos },
        (_, i) => i + 1,
      );
      convergenciaChart.data.datasets[0].data = convLocal;
      convergenciaChart.data.datasets[1].data = convVisita;
      convergenciaChart.data.datasets[2].data = convEmpate;
      convergenciaChart.update();

      // --- Gráfica de throughput por Consumidor ---
      throughputChart.data.datasets[0].data = throughputComponentes;
      throughputChart.update();

      // --- Pastel de distribución ---
      pieChart.data.datasets[0].data = distribucion;
      pieChart.update();

      // --- Últimos resultados ---
      if (data.ultimos_resultados) {
        const tabla = document.querySelector(".tabla-resultados");
        tabla.innerHTML = "";
        data.ultimos_resultados.forEach((res) => {
          const claseCss = res.tipo.toLowerCase();
          tabla.innerHTML += `
            <div class="resultado-fila">
              <span class="res-id">${res.id}</span>
              <span class="res-marcador">${res.marcador}</span>
              <span class="res-resultado ${claseCss}">${res.tipo}</span>
            </div>`;
        });
      }
    } catch (error) {
      console.error("Error cargando datos del dashboard:", error);
    }
  }

  cargarDatosDashboard();
  setInterval(cargarDatosDashboard, 1000);

  console.log(" Dashboard Montecarlo · gráficas cargadas");
});

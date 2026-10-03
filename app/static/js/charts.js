// LifePilot AI Chart.js Light-Themed Renderers

function renderTrendChart(canvasId, chartData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx || !chartData) return;

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: 'Productivity Score',
          data: chartData.productivity,
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.35,
          borderWidth: 3
        },
        {
          label: 'Work Hours',
          data: chartData.work,
          borderColor: '#0EA5E9',
          backgroundColor: 'transparent',
          borderDash: [5, 5],
          tension: 0.35,
          borderWidth: 2
        },
        {
          label: 'Sleep Hours',
          data: chartData.sleep,
          borderColor: '#9333EA',
          backgroundColor: 'transparent',
          tension: 0.35,
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { color: '#0F172A', font: { family: 'Inter', weight: '600' } }
        }
      },
      scales: {
        x: {
          grid: { color: '#E2E8F0' },
          ticks: { color: '#475569', font: { family: 'Inter' } }
        },
        y: {
          grid: { color: '#E2E8F0' },
          ticks: { color: '#475569', font: { family: 'Inter' } },
          min: 0,
          max: 100
        }
      }
    }
  });
}

function renderExpensePieChart(canvasId, categories, amounts) {
  const ctx = document.getElementById(canvasId);
  if (!ctx || !categories.length) return;

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: categories,
      datasets: [{
        data: amounts,
        backgroundColor: [
          '#10B981', '#0EA5E9', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#64748B'
        ],
        borderWidth: 2,
        borderColor: '#FFFFFF'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: { color: '#0F172A', font: { family: 'Inter' } }
        }
      }
    }
  });
}

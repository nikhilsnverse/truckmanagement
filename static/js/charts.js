document.addEventListener('DOMContentLoaded', function () {
  initMonthlyChart();
});

function initMonthlyChart() {
  const canvas = document.getElementById('monthlyChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const incomeData = new Array(12).fill(0);
  const expenseData = new Array(12).fill(0);

  if (typeof monthlyData !== 'undefined' && monthlyData) {
    monthlyData.forEach(function (item) {
      if (!item.month) return;
      const monthStr = item.month;
      const idx = labels.findIndex(function (l) {
        return monthStr.toLowerCase().includes(l.toLowerCase()) ||
               monthStr.includes(String(labels.indexOf(l) + 1).padStart(2, '0'));
      });
      if (idx >= 0) {
        incomeData[idx] = item.income || 0;
        expenseData[idx] = item.expense || 0;
      }
    });
  }

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Income',
          data: incomeData,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16,185,129,0.1)',
          fill: true,
          tension: 0.4,
          borderWidth: 2,
          pointBackgroundColor: '#10b981',
          pointRadius: 3,
          pointHoverRadius: 6
        },
        {
          label: 'Expenses',
          data: expenseData,
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239,68,68,0.05)',
          fill: true,
          tension: 0.4,
          borderWidth: 2,
          pointBackgroundColor: '#ef4444',
          pointRadius: 3,
          pointHoverRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      plugins: {
        legend: {
          position: 'top',
          labels: { usePointStyle: true, padding: 16, font: { size: 12 } }
        },
        tooltip: {
          backgroundColor: 'rgba(0,0,0,0.8)',
          padding: 12,
          cornerRadius: 8,
          callbacks: {
            label: function (ctx) {
              return ctx.dataset.label + ': $' + ctx.parsed.y.toFixed(2);
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(0,0,0,0.05)', drawBorder: false },
          ticks: {
            callback: function (val) { return '$' + val; },
            font: { size: 11 }
          }
        },
        x: {
          grid: { display: false },
          ticks: { font: { size: 11 } }
        }
      }
    }
  });
}

function initManagerChart() {
  const canvas = document.getElementById('managerChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const incomeData = new Array(12).fill(0);
  const expenseData = new Array(12).fill(0);

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Income',
          data: incomeData,
          backgroundColor: 'rgba(16,185,129,0.7)',
          borderRadius: 6
        },
        {
          label: 'Expenses',
          data: expenseData,
          backgroundColor: 'rgba(239,68,68,0.7)',
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { usePointStyle: true, padding: 16 } }
      },
      scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
        x: { grid: { display: false } }
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', function () {
  initStatAnimations();
  initTooltips();
});

function initStatAnimations() {
  const statValues = document.querySelectorAll('.stat-value');
  statValues.forEach(function (el) {
    const text = el.textContent;
    const numMatch = text.match(/[\d,.]+/);
    if (!numMatch) return;
    const target = parseFloat(numMatch[0].replace(/,/g, ''));
    const prefix = text.includes('$') ? '$' : '';
    const suffix = text.includes('km') ? ' km' : '';

    if (target > 100) {
      let current = 0;
      const steps = 30;
      const increment = target / steps;
      const timer = setInterval(function () {
        current += increment;
        if (current >= target) {
          current = target;
          clearInterval(timer);
        }
        const formatted = prefix + Math.floor(current).toLocaleString() + suffix;
        el.textContent = text.replace(/[\d,.]+/, Math.floor(current).toLocaleString());
      }, 30);
      setTimeout(function () {
        clearInterval(timer);
        el.textContent = text;
      }, 1500);
    }
  });
}

function initTooltips() {
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  if (tooltips.length && typeof bootstrap !== 'undefined') {
    tooltips.forEach(function (el) {
      new bootstrap.Tooltip(el);
    });
  }
}

function fetchStats() {
  fetch('/api/stats')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      document.querySelectorAll('[data-stat]').forEach(function (el) {
        const key = el.getAttribute('data-stat');
        if (data[key] !== undefined) {
          el.textContent = data[key];
        }
      });
    })
    .catch(function () {});
}

function loadRecentTrips() {
  const container = document.getElementById('recentTripsContainer');
  if (!container) return;

  fetch('/api/recent-trips')
    .then(function (r) { return r.json(); })
    .then(function (trips) {
      if (trips.length === 0) {
        container.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">No recent trips</td></tr>';
        return;
      }
      let html = '';
      trips.forEach(function (t) {
        html += '<tr>';
        html += '<td><span class="truck-badge">' + (t.truck_number || 'N/A') + '</span></td>';
        html += '<td>' + t.source + ' \u2192 ' + t.destination + '</td>';
        html += '<td>' + (t.driver_name || 'N/A') + '</td>';
        html += '<td><span class="status-badge status-' + t.status.toLowerCase() + '">' + t.status + '</span></td>';
        html += '<td>$' + (t.income || 0).toFixed(2) + '</td>';
        html += '<td>' + (t.created_at ? new Date(t.created_at).toLocaleDateString() : '-') + '</td>';
        html += '</tr>';
      });
      container.innerHTML = html;
    })
    .catch(function () {});
}

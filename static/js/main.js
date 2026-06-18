document.addEventListener('DOMContentLoaded', function () {
  initSidebar();
  initThemeToggle();
  initNotifications();
  initSearch();
  hideLoading();
});

function initSidebar() {
  const toggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
    document.addEventListener('click', function (e) {
      if (window.innerWidth <= 991.98) {
        if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
          sidebar.classList.remove('open');
        }
      }
    });
  }
}

function initThemeToggle() {
  const toggle = document.getElementById('themeToggle');
  const icon = document.getElementById('themeIcon');
  if (!toggle || !icon) return;

  const savedTheme = localStorage.getItem('theme') || 'light';
  applyTheme(savedTheme);

  toggle.addEventListener('click', function () {
    const current = document.documentElement.getAttribute('data-bs-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    localStorage.setItem('theme', next);
  });

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    if (icon) {
      icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
  }
}

function initNotifications() {
  const btn = document.getElementById('notificationBtn');
  const panel = document.getElementById('alertsPanel');
  const closeBtn = document.getElementById('closeAlerts');
  const badge = document.getElementById('alertBadge');
  const body = document.getElementById('alertsBody');

  if (!btn || !panel) return;

  btn.addEventListener('click', function () {
    const isVisible = panel.style.display !== 'none';
    panel.style.display = isVisible ? 'none' : 'block';
    if (!isVisible) fetchAlerts();
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', function () {
      panel.style.display = 'none';
    });
  }

  function fetchAlerts() {
    fetch('/api/alerts')
      .then(r => r.json())
      .then(data => {
        if (!body) return;
        if (data.length === 0) {
          body.innerHTML = '<div class="text-center text-muted py-3"><i class="fas fa-check-circle text-success fa-2x mb-2"></i><p>All clear, no alerts</p></div>';
          if (badge) badge.style.display = 'none';
          return;
        }
        let html = '';
        data.forEach(function (alert) {
          const isUrgent = alert.days_left <= 7;
          html += '<div class="alert-item">';
          html += '<div class="alert-icon ' + (isUrgent ? 'bg-danger' : 'bg-warning') + '"><i class="fas fa-exclamation"></i></div>';
          html += '<div class="alert-content">';
          html += '<span class="alert-title">' + alert.truck + ' - ' + alert.type + '</span>';
          html += '<span class="alert-desc">Expires ' + alert.expires + ' (' + alert.days_left + ' days left)</span>';
          html += '</div></div>';
        });
        body.innerHTML = html;
        if (badge) {
          badge.textContent = data.length;
          badge.style.display = 'flex';
        }
      })
      .catch(function () {
        if (body) body.innerHTML = '<div class="text-center text-muted py-3">Failed to load alerts</div>';
      });
  }

  fetchAlerts();
}

function initSearch() {
  const input = document.getElementById('globalSearch');
  if (!input) return;

  let timeout;
  input.addEventListener('input', function () {
    clearTimeout(timeout);
    timeout = setTimeout(function () {
      const q = input.value.trim().toLowerCase();
      if (q.length < 2) return;
      const rows = document.querySelectorAll('.table-custom tbody tr');
      rows.forEach(function (row) {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(q) ? '' : 'none';
      });
    }, 300);
  });
}

function showLoading() {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) overlay.classList.add('active');
}

function hideLoading() {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) overlay.classList.remove('active');
}

document.addEventListener('submit', function () {
  showLoading();
});

window.addEventListener('beforeunload', function () {
  showLoading();
});

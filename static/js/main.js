// TTTI ERMS - Main JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('show');
            } else {
                sidebar.classList.toggle('collapsed');
                if (sidebar.classList.contains('collapsed')) {
                    sidebar.style.width = '0';
                    mainContent.style.marginLeft = '0';
                } else {
                    sidebar.style.width = '260px';
                    mainContent.style.marginLeft = '260px';
                }
            }
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // Confirm delete forms
    document.querySelectorAll('form[onsubmit]').forEach(function (form) {
        // Already handled inline
    });

    // DataTable-like sorting for tables (simple)
    document.querySelectorAll('table.sortable th').forEach(function (th) {
        th.style.cursor = 'pointer';
        th.addEventListener('click', function () {
            const table = th.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const idx = Array.from(th.parentNode.children).indexOf(th);
            const asc = th.dataset.sort !== 'asc';
            th.dataset.sort = asc ? 'asc' : 'desc';

            rows.sort(function (a, b) {
                const aText = (a.cells[idx] ? a.cells[idx].textContent : '').trim();
                const bText = (b.cells[idx] ? b.cells[idx].textContent : '').trim();
                return asc ? aText.localeCompare(bText) : bText.localeCompare(aText);
            });

            rows.forEach(function (row) { tbody.appendChild(row); });
        });
    });
});

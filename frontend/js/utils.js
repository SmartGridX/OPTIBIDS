// utils.js — Shared toast helper for auth pages

function showToast(msg, type='info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const icons = { success:'fa-check-circle', error:'fa-times-circle', info:'fa-info-circle' };
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<i class="fas ${icons[type] || 'fa-info-circle'}"></i><span>${msg}</span>`;
  container.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

window.showToast = showToast;

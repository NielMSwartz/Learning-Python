(function () {
  'use strict';
  const esc = PA.escapeHtml;
  let timer = null;

  function query() {
    const params = new URLSearchParams();
    const q = document.getElementById('challenge-search').value.trim();
    if (q) params.set('q', q);
    const level = document.getElementById('level-filter').value;
    if (level) params.set('level', level);
    const category = document.getElementById('category-filter').value;
    if (category) params.set('category', category);
    return params.toString();
  }

  async function load() {
    try {
      const data = await PA.api('/api/challenges?' + query());
      const select = document.getElementById('category-filter');
      const current = select.value;
      select.innerHTML = '<option value="">All categories</option>' + data.categories.map(c =>
        `<option value="${esc(c)}" ${c === current ? 'selected' : ''}>${esc(c)}</option>`).join('');
      document.getElementById('challenge-grid').innerHTML = data.challenges.length ? data.challenges.map(c =>
        `<div class="card project-card">
          <div class="card-top"><h3><a href="/challenges/${c.slug}" style="color:var(--text)">${esc(c.title)}</a></h3></div>
          <p>${esc(c.description)}</p>
          <div class="meta">
            <span class="badge ${c.level === 1 ? 'green' : c.level === 2 ? 'blue' : c.level === 3 ? 'yellow' : 'red'}">L${c.level}</span>
            <span class="badge">${esc(c.category)}</span>
            <span class="badge yellow">${'★'.repeat(c.difficulty)}</span>
            <span class="badge">${c.points} pts</span>
            ${c.completed ? '<span class="badge green">✓ Solved</span>' : ''}
          </div>
          <a class="btn btn-ghost btn-sm" href="/challenges/${c.slug}">${c.completed ? 'Review' : 'Solve challenge'} →</a>
        </div>`).join('') : '<p class="muted">No challenges match those filters.</p>';
    } catch (err) { PA.toast(err.message, 'error'); }
  }

  document.addEventListener('DOMContentLoaded', () => {
    load();
    document.getElementById('challenge-search').addEventListener('input', () => {
      clearTimeout(timer); timer = setTimeout(load, 220);
    });
    document.getElementById('level-filter').addEventListener('change', load);
    document.getElementById('category-filter').addEventListener('change', load);
  });
})();

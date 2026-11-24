(function () {
  'use strict';
  const esc = PA.escapeHtml;

  function continueMarkup(item) {
    if (!item) {
      return '<a class="btn btn-accent" href="/learn">Choose your first project →</a>';
    }
    const path = item.type === 'project' ? `/learn/project/${item.slug}`
      : item.type === 'challenge' ? `/challenges/${item.slug}`
      : `/practice/${item.slug}`;
    return `<a class="btn btn-accent" href="${path}">Continue ${esc(item.title)} →</a>
            <span class="badge blue">${esc(item.type)} · ${item.score}%</span>`;
  }

  function rowMarkup(item) {
    const path = item.type === 'project' ? `/learn/project/${item.slug}` : `/challenges/${item.slug}`;
    const done = item.status === 'completed';
    return `<a href="${path}" style="display:flex;gap:10px;align-items:center;padding:10px;border:1px solid var(--line);border-radius:10px;color:var(--text)">
      <span class="badge ${done ? 'green' : 'blue'}">${done ? '✓' : '→'}</span>
      <span style="flex:1"><strong>${esc(item.title)}</strong><br><span class="muted small">${esc(item.type)} · Level ${item.level || 1}</span></span>
      <span class="small muted">${item.score || 0}%</span></a>`;
  }

  document.addEventListener('DOMContentLoaded', async () => {
    try {
      const { dashboard: data } = await PA.api('/api/dashboard');
      const s = data.stats;
      document.getElementById('hero-streak').textContent = `${s.streak} day${s.streak === 1 ? '' : 's'} in a row`;
      document.getElementById('stat-level').textContent = `L${data.level.current}`;
      document.getElementById('stat-hours').textContent = s.coding_hours;
      document.getElementById('stat-projects').textContent = `${s.projects_completed}/${s.projects_total}`;
      document.getElementById('stat-exercises').textContent = s.exercises_completed;
      document.getElementById('module-name').textContent = `Level ${data.current_module.level} · ${data.current_module.name}`;
      document.getElementById('module-progress-count').textContent = `${data.current_module.progress}/${data.current_module.total}`;
      document.getElementById('module-progress-bar').style.width =
        (data.current_module.total ? 100 * data.current_module.progress / data.current_module.total : 0) + '%';

      document.getElementById('continue-area').innerHTML = continueMarkup(data.continue_learning);
      document.getElementById('recent-projects').innerHTML = data.recent_projects.length
        ? data.recent_projects.map(rowMarkup).join('')
        : '<span class="muted small">No projects yet — start with the learning pathway.</span>';
      document.getElementById('recommended').innerHTML = data.recommended_challenges.length
        ? data.recommended_challenges.map(c => `<a href="/challenges/${c.slug}" style="display:flex;gap:10px;align-items:center;padding:10px;border:1px solid var(--line);border-radius:10px;color:var(--text)">
            <span class="badge yellow">★ ${c.difficulty}</span><span style="flex:1"><strong>${esc(c.title)}</strong><br><span class="muted small">${esc(c.category)} · ${c.points} pts</span></span></a>`).join('')
        : '<span class="muted small">Complete a project to unlock more challenges.</span>';

      document.getElementById('achievement-grid').innerHTML = data.achievements.length
        ? data.achievements.map(a => `<div class="card" style="text-align:center;opacity:${a.earned_at ? 1 : .45}">
            <div style="font-size:28px">${a.icon}</div><strong class="small">${esc(a.name)}</strong>
            <p class="muted tiny" style="margin:4px 0 0">${esc(a.description)}</p></div>`).join('')
        : '<span class="muted small">No achievements defined yet.</span>';
    } catch (err) {
      PA.toast(err.message, 'error');
    }
  });
})();

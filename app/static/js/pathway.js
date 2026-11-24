(function () {
  'use strict';
  const esc = PA.escapeHtml;

  function projectCard(project) {
    const locked = !project.unlocked;
    const badge = project.completed ? '<span class="badge green">✓ Completed</span>'
      : project.status === 'in_progress' ? '<span class="badge yellow">In progress</span>'
      : locked ? '<span class="badge locked">🔒 Locked</span>' : '<span class="badge blue">Available</span>';
    const action = locked
      ? '<button class="btn btn-ghost btn-sm" disabled>Complete previous project</button>'
      : `<a class="btn ${project.completed ? 'btn-ghost' : 'btn-primary'} btn-sm" href="/learn/project/${project.slug}">${project.completed ? 'Review' : 'Open project'} →</a>`;
    return `<div class="card project-card ${locked ? 'locked' : ''}">
      <div class="card-top"><span class="level-dot"></span><h3>${esc(project.title)}</h3></div>
      <p>${esc(project.subtitle || project.summary || '')}</p>
      <div class="meta">${badge}<span class="badge">${project.estimated_minutes} min</span>${project.score ? `<span class="badge blue">Best ${project.score}%</span>` : ''}</div>
      <div class="progress thin"><span style="width:${project.completed ? 100 : project.score || 0}%"></span></div>
      ${action}
    </div>`;
  }

  function levelBlock(level) {
    const pct = level.project_count ? 100 * level.completed_count / level.project_count : 0;
    return `<section class="level-block ${level.unlocked ? '' : 'locked'}">
      <div class="level-header">
        <div class="level-number">${level.level}</div>
        <div><h2 style="margin:0">Level ${level.level} · ${esc(level.name)}</h2><span class="muted small">${esc(level.requirement)}</span></div>
        <span class="spacer" style="flex:1"></span>
        <span class="badge ${level.unlocked ? 'blue' : 'locked'}">${level.unlocked ? 'Unlocked' : 'Locked'}</span>
        <span class="small muted">${level.completed_count}/${level.project_count} projects</span>
      </div>
      <div class="progress" style="margin-bottom:14px"><span style="width:${pct}%"></span></div>
      <div class="grid cols-3">${level.projects.map(projectCard).join('')}</div>
    </section>`;
  }

  document.addEventListener('DOMContentLoaded', async () => {
    try {
      const { levels } = await PA.api('/api/pathway');
      document.getElementById('levels').innerHTML = levels.map(levelBlock).join('');
    } catch (err) { PA.toast(err.message, 'error'); }
  });
})();

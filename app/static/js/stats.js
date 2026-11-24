(function () {
  'use strict';
  const esc = PA.escapeHtml;

  function lineChart(series) {
    const width = 900, height = 200, padX = 34, padY = 22;
    const values = series.map(d => Math.round(d.seconds / 60));
    const max = Math.max(10, ...values);
    const stepX = (width - padX * 2) / Math.max(1, series.length - 1);
    const points = values.map((value, i) => [padX + i * stepX, height - padY - (value / max) * (height - padY * 2)]);
    const line = points.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(' ');
    const area = `${line} L${points[points.length - 1][0].toFixed(1)},${height - padY} L${padX},${height - padY} Z`;
    const grid = [0, 0.5, 1].map(f => {
      const y = height - padY - f * (height - padY * 2);
      return `<line class="chart-grid" x1="${padX}" x2="${width - padX}" y1="${y}" y2="${y}"/>` +
        `<text class="chart-label" x="4" y="${y + 4}">${Math.round(f * max)}m</text>`;
    }).join('');
    const labels = series.map((d, i) => (i % 7 === 0 || i === series.length - 1)
      ? `<text class="chart-label" x="${points[i][0]}" y="${height - 4}" text-anchor="middle">${d.date.slice(5)}</text>` : '').join('');
    return `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Coding activity in the last 30 days">
      <defs><linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#4a9bd6" stop-opacity=".7"/><stop offset="100%" stop-color="#4a9bd6" stop-opacity="0"/>
      </linearGradient></defs>
      ${grid}<path class="chart-area" d="${area}"/><path class="chart-line" d="${line}"/>${labels}
      ${points.map((p, i) => `<circle cx="${p[0]}" cy="${p[1]}" r="2.5" fill="var(--yellow)"><title>${series[i].date}: ${values[i]} min</title></circle>`).join('')}
    </svg>`;
  }

  function bars(items, empty) {
    if (!items.length) return `<p class="muted small">${empty}</p>`;
    const max = Math.max(...items.map(i => i.average), 1);
    return items.map(item => `<div>
      <div class="progress-row"><span>${esc(item.category)}</span><strong>${item.average}% · ${item.attempts} attempts</strong></div>
      <div class="progress"><span style="width:${Math.max(3, 100 * item.average / max)}%"></span></div>
    </div>`).join('');
  }

  document.addEventListener('DOMContentLoaded', async () => {
    try {
      const { stats: data } = await PA.api('/api/stats');
      const t = data.totals;
      const cards = document.querySelectorAll('#totals .stat-value');
      cards[0].textContent = `${t.projects}/21`;
      cards[1].textContent = `${t.challenges}/24`;
      cards[2].textContent = t.coding_hours;
      cards[3].textContent = `${t.success_rate}%`;
      document.getElementById('activity-chart').innerHTML = lineChart(data.activity);
      document.getElementById('strong-areas').innerHTML = bars(data.strong_areas, 'Solve more challenges to reveal your strengths.');
      document.getElementById('weak-areas').innerHTML = bars(data.weak_areas, 'No weak areas identified yet — keep it up.');
      document.getElementById('level-progress').innerHTML = data.level_progress.map(level => `
        <div class="${level.unlocked ? '' : 'muted'}">
          <div class="progress-row"><span>Level ${level.level} · ${esc(level.name)}</span><strong>${level.completed_count}/${level.project_count}</strong></div>
          <div class="progress thin"><span style="width:${level.project_count ? 100 * level.completed_count / level.project_count : 0}%"></span></div>
        </div>`).join('');
      document.getElementById('recommendations').innerHTML = data.recommendations.length ? data.recommendations.map(r => {
        const href = r.type === 'project' ? '/learn' : '/challenges/' + esc(r.slug);
        return `<a href="${href}" class="topic-chip"><span>→</span><span><strong>${esc(r.title)}</strong><br><span class="muted">${esc(r.reason)}</span></span></a>`;
      }).join('') : '<p class="muted small">You are all caught up. Try a challenge from the library.</p>';
      const earned = data.achievements.filter(a => a.earned_at).length;
      document.getElementById('achievement-count').textContent = `${earned} of ${data.achievements.length} unlocked`;
      document.getElementById('achievement-grid').innerHTML = data.achievements.map(a => `
        <div class="card" style="text-align:center;opacity:${a.earned_at ? 1 : .45}">
          <div style="font-size:30px">${esc(a.icon)}</div>
          <strong class="small">${esc(a.name)}</strong>
          <p class="muted tiny" style="margin:4px 0 0">${esc(a.description)}</p>
          ${a.earned_at ? `<span class="badge green" style="margin-top:8px">Unlocked</span>` : '<span class="badge" style="margin-top:8px">Locked</span>'}
        </div>`).join('');
    } catch (err) { PA.toast(err.message, 'error'); }
  });
})();

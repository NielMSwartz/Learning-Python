(function () {
  'use strict';
  const esc = PA.escapeHtml;

  document.addEventListener('DOMContentLoaded', async () => {
    const parts = location.pathname.split('/').filter(Boolean);
    const slug = parts[parts.length - 1];
    try {
      const { topic } = await PA.api('/api/library/' + encodeURIComponent(slug));
      document.title = `${topic.title} · Python Academy`;
      document.getElementById('topic-title').textContent = topic.title;
      document.getElementById('topic-summary').textContent = topic.summary;
      document.getElementById('topic-explanation').innerHTML = topic.explanation
        .split('\n\n').map(p => `<p>${esc(p).replace(/`([^`]+)`/g, '<code class="mono text-yellow">$1</code>')}</p>`).join('');
      document.getElementById('topic-why').textContent = topic.why_useful;
      document.getElementById('topic-mistakes').innerHTML = (topic.mistakes || [])
        .map(m => `<li><span>${esc(m)}</span></li>`).join('');
      document.getElementById('topic-examples').innerHTML = (topic.examples || []).map(example =>
        `<div><pre class="mono small" style="background:var(--bg);border:1px solid var(--line);padding:12px;border-radius:10px;overflow:auto">${esc(example.code)}</pre>
         <p class="muted small" style="margin-top:8px">${esc(example.explanation)}</p></div>`).join('');
      const exercise = (topic.exercises || [])[0];
      document.getElementById('exercise-link').innerHTML = exercise
        ? `<a class="btn btn-accent" href="/practice/${exercise.slug}">Start practice exercise →</a>`
        : '<span class="muted">No exercise attached to this topic yet.</span>';
      const button = document.getElementById('bookmark-topic');
      const setBookmark = value => {
        button.textContent = value ? '★ Bookmarked' : '☆ Bookmark';
        button.classList.toggle('btn-accent', value);
      };
      setBookmark(topic.bookmarked);
      button.addEventListener('click', async () => {
        try {
          const data = await PA.api(`/api/library/${topic.id}/bookmark`, { method: 'POST' });
          setBookmark(data.bookmarked);
        } catch (err) { PA.toast(err.message, 'error'); }
      });
    } catch (err) { PA.toast(err.message, 'error'); }
  });
})();

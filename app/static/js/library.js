(function () {
  'use strict';
  const esc = PA.escapeHtml;
  let topics = [];
  let category = '';
  let bookmarkedOnly = false;
  let timer = null;

  function query() {
    const params = new URLSearchParams();
    const q = document.getElementById('library-search').value.trim();
    if (q) params.set('q', q);
    const level = document.getElementById('level-filter').value;
    if (level) params.set('level', level);
    if (category) params.set('category', category);
    if (bookmarkedOnly) params.set('bookmarked', '1');
    return params.toString();
  }

  async function load() {
    try {
      const data = await PA.api('/api/library?' + query());
      topics = data.topics;
      const chips = document.getElementById('category-chips');
      chips.innerHTML = ['', ...data.categories].map(c =>
        `<button class="chip ${category === c ? 'active' : ''}" data-category="${esc(c)}">${c || 'All categories'}</button>`).join('');
      chips.querySelectorAll('[data-category]').forEach(button => button.addEventListener('click', () => {
        category = button.dataset.category; load();
      }));
      document.getElementById('topic-grid').innerHTML = topics.length ? topics.map(t =>
        `<div class="card">
          <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px">
            <span class="badge blue">L${t.level}</span><span class="badge">${esc(t.category)}</span>
            <span style="flex:1"></span>
            <button class="icon-button bookmark-btn" data-id="${t.id}" title="Bookmark">${t.bookmarked ? '★' : '☆'}</button>
          </div>
          <h3><a href="/library/${t.slug}" style="color:var(--text)">${esc(t.title)}</a></h3>
          <p class="muted small">${esc(t.summary)}</p>
          <a class="small" href="/library/${t.slug}">Open topic →</a>
        </div>`).join('') : '<p class="muted">No topics match those filters.</p>';
      document.querySelectorAll('.bookmark-btn').forEach(button => button.addEventListener('click', async () => {
        try {
          const data = await PA.api(`/api/library/${button.dataset.id}/bookmark`, { method: 'POST' });
          button.textContent = data.bookmarked ? '★' : '☆';
          PA.toast(data.bookmarked ? 'Bookmarked for revision.' : 'Bookmark removed.', 'success');
        } catch (err) { PA.toast(err.message, 'error'); }
      }));
    } catch (err) { PA.toast(err.message, 'error'); }
  }

  document.addEventListener('DOMContentLoaded', () => {
    load();
    document.getElementById('library-search').addEventListener('input', () => {
      clearTimeout(timer); timer = setTimeout(load, 220);
    });
    document.getElementById('level-filter').addEventListener('change', load);
    const bookmarkFilter = document.getElementById('bookmark-filter');
    bookmarkFilter.addEventListener('click', () => {
      bookmarkedOnly = !bookmarkedOnly;
      bookmarkFilter.classList.toggle('btn-accent', bookmarkedOnly);
      load();
    });
  });
})();

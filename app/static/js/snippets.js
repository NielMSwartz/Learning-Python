(function () {
  'use strict';
  const esc = PA.escapeHtml;
  let snippets = [];
  let timer = null;
  let editor = null;

  function query() {
    const params = new URLSearchParams();
    const q = document.getElementById('snippet-search').value.trim();
    if (q) params.set('q', q);
    const category = document.getElementById('category-filter').value;
    if (category) params.set('category', category);
    const tag = document.getElementById('tag-filter').value.trim();
    if (tag) params.set('tag', tag);
    return params.toString();
  }

  async function load() {
    try {
      const data = await PA.api('/api/snippets?' + query());
      snippets = data.snippets;
      const select = document.getElementById('category-filter');
      const current = select.value;
      select.innerHTML = '<option value="">All categories</option>' + data.categories.map(c =>
        `<option value="${esc(c)}" ${c === current ? 'selected' : ''}>${esc(c)}</option>`).join('');
      const grid = document.getElementById('snippet-grid');
      grid.innerHTML = snippets.length ? snippets.map(s => `
        <div class="card snippet-card">
          <div class="meta">
            <span class="badge blue">${esc(s.category)}</span>
            ${(s.tags || []).map(t => `<span class="badge">#${esc(t)}</span>`).join('')}
          </div>
          <h3>${esc(s.name)}</h3>
          <p class="muted small">${esc(s.description) || 'No description'}</p>
          <pre>${esc(s.code)}</pre>
          <div class="button-row" style="margin-top:12px">
            <button class="btn btn-ghost btn-sm" data-copy="${s.id}">Copy</button>
            <button class="btn btn-ghost btn-sm" data-edit="${s.id}">Edit</button>
            <button class="btn btn-danger btn-sm" data-delete="${s.id}">Delete</button>
          </div>
        </div>`).join('') : '<p class="muted">No snippets yet. Save something from the playground or create one here.</p>';

      grid.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
        const snippet = snippets.find(s => s.id === Number(button.dataset.copy));
        try {
          await navigator.clipboard.writeText(snippet.code);
          PA.toast('Snippet copied to clipboard.', 'success');
        } catch (err) { PA.toast('Clipboard is unavailable in this browser.', 'error'); }
      }));
      grid.querySelectorAll('[data-edit]').forEach(button => button.addEventListener('click', () => openModal(snippets.find(s => s.id === Number(button.dataset.edit)))));
      grid.querySelectorAll('[data-delete]').forEach(button => button.addEventListener('click', async () => {
        if (!confirm('Delete this snippet permanently?')) return;
        try {
          await PA.api('/api/snippets/' + button.dataset.delete, { method: 'DELETE' });
          PA.toast('Snippet deleted.');
          load();
        } catch (err) { PA.toast(err.message, 'error'); }
      }));
    } catch (err) { PA.toast(err.message, 'error'); }
  }

  function openModal(snippet) {
    const data = snippet || {};
    document.getElementById('modal-title').textContent = snippet ? 'Edit snippet' : 'New snippet';
    document.getElementById('snippet-id').value = snippet ? snippet.id : '';
    document.getElementById('snippet-name').value = snippet ? snippet.name : '';
    document.getElementById('snippet-description').value = snippet ? snippet.description : '';
    document.getElementById('snippet-category').value = snippet ? snippet.category : 'General';
    document.getElementById('snippet-tags').value = snippet ? (snippet.tags || []).join(', ') : '';
    document.getElementById('snippet-error').textContent = '';
    editor.setValue(snippet ? snippet.code : '');
    PA.showModal('snippet-modal');
  }

  document.addEventListener('DOMContentLoaded', () => {
    editor = PA.createEditor(document.getElementById('snippet-code'), {
      height: '180px', lineWrapping: true
    });
    load();
    document.getElementById('new-snippet').addEventListener('click', () => openModal(null));
    document.getElementById('close-modal').addEventListener('click', () => PA.hideModal('snippet-modal'));
    document.getElementById('cancel-modal').addEventListener('click', () => PA.hideModal('snippet-modal'));
    document.getElementById('snippet-modal').addEventListener('click', event => {
      if (event.target.id === 'snippet-modal') PA.hideModal('snippet-modal');
    });
    ['snippet-search', 'category-filter', 'tag-filter'].forEach(id => {
      const element = document.getElementById(id);
      element.addEventListener(id === 'snippet-search' ? 'input' : 'change', () => {
        clearTimeout(timer); timer = setTimeout(load, 200);
      });
    });
    document.getElementById('save-modal').addEventListener('click', async () => {
      const id = document.getElementById('snippet-id').value;
      const payload = {
        name: document.getElementById('snippet-name').value.trim() || 'Untitled snippet',
        code: editor.getValue(),
        description: document.getElementById('snippet-description').value,
        category: document.getElementById('snippet-category').value.trim() || 'General',
        tags: document.getElementById('snippet-tags').value
      };
      try {
        await PA.api(id ? '/api/snippets/' + id : '/api/snippets', {
          method: id ? 'PUT' : 'POST', body: payload
        });
        PA.hideModal('snippet-modal');
        PA.toast('Snippet saved.', 'success');
        load();
      } catch (err) { document.getElementById('snippet-error').textContent = err.message; }
    });
  });
})();

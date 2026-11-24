(function () {
  'use strict';
  const esc = PA.escapeHtml;
  let editor = null;
  let controller = null;

  async function run() {
    if (controller) return;
    controller = new AbortController();
    document.getElementById('run-btn').disabled = true;
    document.getElementById('stop-btn').disabled = false;
    const output = document.getElementById('console-output');
    output.textContent = 'Running…';
    try {
      const data = await PA.api('/api/execute', { method: 'POST', signal: controller.signal, body: {
        code: editor.getValue(), stdin: document.getElementById('stdin-input').value
      }});
      output.innerHTML = data.stdout ? esc(data.stdout) : '<span class="empty-console">(no output)</span>';
      const errors = document.getElementById('console-errors');
      errors.textContent = [data.error, data.stderr].filter(Boolean).join('\n') || 'No errors.';
      if (data.error || data.stderr) document.querySelector('[data-console-tab="errors"]').classList.add('active');
    } catch (err) {
      output.textContent = err.name === 'AbortError' ? 'Execution stopped.' : err.message;
    } finally {
      controller = null;
      document.getElementById('run-btn').disabled = false;
      document.getElementById('stop-btn').disabled = true;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    editor = PA.createEditor(document.getElementById('code-input'), {
      height: '440px', lineWrapping: true, onRun: run
    });
    editor.setValue('# Try something in Python\nfor number in range(1, 6):\n    print(f"{number} squared is {number ** 2}")\n');

    document.getElementById('run-btn').addEventListener('click', run);
    document.getElementById('stop-btn').addEventListener('click', () => controller && controller.abort());
    document.getElementById('format-btn').addEventListener('click', async () => {
      try {
        const data = await PA.api('/api/format', { method: 'POST', body: { code: editor.getValue() } });
        editor.setValue(data.code);
        PA.toast('Code formatted.', 'success');
      } catch (err) { PA.toast(err.message, 'error'); }
    });
    document.getElementById('clear-btn').addEventListener('click', () => {
      document.getElementById('console-output').innerHTML = '<span class="empty-console">Console cleared.</span>';
      document.getElementById('console-errors').innerHTML = '<span class="empty-console">No errors.</span>';
    });
    document.querySelectorAll('[data-console-tab]').forEach(button => button.addEventListener('click', () => {
      ['output', 'errors'].forEach(name => {
        document.getElementById('console-' + name).style.display = name === button.dataset.consoleTab ? 'block' : 'none';
        document.querySelector(`[data-console-tab="${name}"]`).classList.toggle('active', name === button.dataset.consoleTab);
      });
    }));

    const modal = document.getElementById('snippet-modal');
    document.getElementById('save-snippet').addEventListener('click', () => PA.showModal('snippet-modal'));
    ['close-modal', 'cancel-modal'].forEach(id => document.getElementById(id).addEventListener('click', () => PA.hideModal('snippet-modal')));
    modal.addEventListener('click', event => { if (event.target === modal) PA.hideModal('snippet-modal'); });
    document.getElementById('confirm-save').addEventListener('click', async () => {
      const error = document.getElementById('snippet-error');
      error.textContent = '';
      try {
        await PA.api('/api/snippets', { method: 'POST', body: {
          name: document.getElementById('snippet-name').value.trim() || 'Untitled snippet',
          description: document.getElementById('snippet-description').value,
          category: document.getElementById('snippet-category').value.trim() || 'General',
          tags: document.getElementById('snippet-tags').value,
          code: editor.getValue()
        }});
        PA.hideModal('snippet-modal');
        PA.toast('Snippet saved to your library.', 'success');
        ['snippet-name', 'snippet-description', 'snippet-tags'].forEach(id => document.getElementById(id).value = '');
      } catch (err) { error.textContent = err.message; }
    });
  });
})();

/* Python Academy — shared frontend utilities */
(function () {
  'use strict';

  const TOKEN = document.querySelector('meta[name="csrf-token"]')?.content || '';

  async function api(path, options = {}) {
    const init = {
      method: options.method || 'GET',
      credentials: 'same-origin',
      headers: { Accept: 'application/json' },
      signal: options.signal || null
    };
    if (options.body !== undefined) {
      init.headers['Content-Type'] = 'application/json';
      init.body = JSON.stringify(options.body);
    }
    if (!['GET', 'HEAD'].includes(init.method.toUpperCase())) {
      init.headers['X-CSRF-Token'] = TOKEN;
    }
    const response = await fetch(path, init);
    let data = {};
    try { data = await response.json(); } catch (_) { /* non-JSON response */ }
    if (!response.ok) {
      const message = (data.error && data.error.message) || `Request failed (${response.status})`;
      const err = new Error(message);
      err.status = response.status;
      throw err;
    }
    return data;
  }

  function toast(message, type = '') {
    const stack = document.getElementById('toast-stack') || (() => {
      const el = document.createElement('div');
      el.id = 'toast-stack';
      el.className = 'toast-stack';
      document.body.appendChild(el);
      return el;
    })();
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = message;
    stack.appendChild(el);
    setTimeout(() => el.remove(), 4200);
  }

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, ch => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[ch]));
  }

  const KEYWORDS = [
    'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del',
    'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global', 'if', 'import',
    'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
    'True', 'while', 'with', 'yield', 'print', 'len', 'range', 'enumerate', 'zip', 'str',
    'int', 'float', 'list', 'dict', 'set', 'tuple', 'sum', 'sorted', 'self'
  ];

  function pythonHint(editor) {
    const cursor = editor.getCursor();
    const token = editor.getTokenAt(cursor);
    const start = token.start;
    const end = cursor.ch;
    const current = token.string || '';
    const localWords = new Set();
    const regexp = /\b[A-Za-z_][A-Za-z0-9_]{2,}\b/g;
    let match;
    while ((match = regexp.exec(editor.getValue())) !== null) localWords.add(match[0]);
    const words = [...new Set([...KEYWORDS, ...localWords])].filter(w => w.startsWith(current) && w !== current);
    return { list: words.slice(0, 20), from: CodeMirror.Pos(cursor.line, start), to: CodeMirror.Pos(cursor.line, end) };
  }

  function createEditor(textarea, options = {}) {
    const body = document.body;
    const fontSize = Number(body.dataset.fontSize || 14);
    const tabSize = Number(body.dataset.tabSize || 4);
    const cm = CodeMirror.fromTextArea(textarea, {
      mode: 'python',
      theme: 'material',
      lineNumbers: true,
      indentUnit: tabSize,
      tabSize,
      indentWithTabs: false,
      autoCloseBrackets: true,
      matchBrackets: true,
      lineWrapping: options.lineWrapping ?? body.dataset.lineWrap === '1',
      hintOptions: { hint: pythonHint, completeSingle: false },
      extraKeys: {
        'Ctrl-Enter': () => options.onRun && options.onRun(),
        'Cmd-Enter': () => options.onRun && options.onRun(),
        'Ctrl-S': () => options.onSave && options.onSave(),
        'Cmd-S': () => options.onSave && options.onSave(),
        'Ctrl-/': 'toggleComment',
        'Cmd-/': 'toggleComment',
        'Ctrl-Space': 'autocomplete',
        Tab: cm => {
          if (cm.somethingSelected()) cm.indentSelection('add');
          else cm.replaceSelection(' '.repeat(tabSize), 'end');
        },
        'Shift-Tab': cm => cm.indentSelection('subtract')
      }
    });
    cm.getWrapperElement().style.fontSize = `${fontSize}px`;
    if (options.height) cm.setSize('100%', options.height);
    if (options.onChange) cm.on('change', options.onChange);
    if (options.onCursor) {
      cm.on('cursorActivity', options.onCursor);
      options.onCursor(cm);
    }
    return cm;
  }

  function showModal(id) { document.getElementById(id)?.classList.add('open'); }
  function hideModal(id) { document.getElementById(id)?.classList.remove('open'); }

  function initShell() {
    const sidebar = document.getElementById('sidebar');
    document.getElementById('menu-toggle')?.addEventListener('click', () => sidebar?.classList.toggle('open'));
    document.addEventListener('click', event => {
      if (sidebar?.classList.contains('open') && !sidebar.contains(event.target)
          && !event.target.closest('#menu-toggle')) sidebar.classList.remove('open');
    });

    document.getElementById('theme-toggle')?.addEventListener('click', async () => {
      const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = next;
      try {
        await api('/api/me/preferences', { method: 'PATCH', body: { theme: next } });
      } catch (err) { toast(err.message, 'error'); }
    });

    let deferredInstall = null;
    window.addEventListener('beforeinstallprompt', event => {
      event.preventDefault();
      deferredInstall = event;
      document.getElementById('install-banner')?.classList.add('show');
    });
    document.getElementById('install-btn')?.addEventListener('click', async () => {
      if (!deferredInstall) return;
      deferredInstall.prompt();
      await deferredInstall.userChoice;
      deferredInstall = null;
      document.getElementById('install-banner')?.classList.remove('show');
    });
    document.getElementById('install-dismiss')?.addEventListener('click', () => {
      document.getElementById('install-banner')?.classList.remove('show');
    });

    if ('serviceWorker' in navigator && location.protocol !== 'file:') {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(() => {});
      });
    }

    if (document.body.dataset.coding === '1') {
      setInterval(() => {
        if (document.visibilityState === 'visible') {
          api('/api/activity', { method: 'POST', body: { seconds: 60 } }).catch(() => {});
        }
      }, 60000);
    }
  }

  document.addEventListener('DOMContentLoaded', initShell);

  window.PA = { api, toast, escapeHtml, createEditor, showModal, hideModal };
})();

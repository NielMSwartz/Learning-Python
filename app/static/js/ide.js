(function () {
  'use strict';
  const esc = PA.escapeHtml;
  let projects = [];
  let project = null;
  let files = {};        // path -> { id, content }
  let activePath = null;
  let editor = null;
  let controller = null;
  let dirty = false;

  function markDirty(value) {
    dirty = value;
    document.getElementById('save-state').textContent = value ? 'Unsaved changes' : 'All changes saved';
    document.getElementById('save-state').style.color = value ? 'var(--yellow)' : '';
  }

  function syncCurrent() {
    if (activePath && files[activePath] && editor) files[activePath].content = editor.getValue();
  }

  function renderFileTree() {
    const tree = document.getElementById('file-tree');
    tree.innerHTML = Object.keys(files).sort().map(path =>
      `<button class="file-item ${path === activePath ? 'active' : ''}" data-path="${esc(path)}">
         <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2h9l5 5v15H6z"/></svg>
         <span class="name">${esc(path)}</span></button>`).join('');
    tree.querySelectorAll('[data-path]').forEach(button => button.addEventListener('click', () => openFile(button.dataset.path)));
    document.getElementById('status-file').textContent = activePath || 'No file';
    document.getElementById('project-info').textContent = `${Object.keys(files).length} file(s) · ${project ? esc(project.name) : ''}`;
  }

  function renderTabs() {
    document.getElementById('editor-tabs').innerHTML = Object.keys(files).sort().map(path =>
      `<button class="editor-tab ${path === activePath ? 'active' : ''}" data-path="${esc(path)}">${esc(path)}</button>`).join('');
    document.querySelectorAll('.editor-tab').forEach(button => button.addEventListener('click', () => openFile(button.dataset.path)));
  }

  function openFile(path) {
    if (!files[path]) return;
    syncCurrent();
    activePath = path;
    editor.setValue(files[path].content);
    editor.focus();
    renderFileTree();
    renderTabs();
  }

  async function loadProjects() {
    try {
      const data = await PA.api('/api/ide/projects');
      projects = data.projects;
      if (!projects.length) {
        const created = await PA.api('/api/ide/projects', { method: 'POST', body: { name: 'My first project' } });
        projects = [created.project];
      }
      const select = document.getElementById('project-select');
      select.innerHTML = projects.map(p => `<option value="${p.id}">${esc(p.name)}</option>`).join('');
      await openProject(projects[0].id);
    } catch (err) { PA.toast(err.message, 'error'); }
  }

  async function openProject(id) {
    try {
      syncCurrent();
      const data = await PA.api(`/api/ide/projects/${id}`);
      project = data.project;
      files = {};
      data.project.files.forEach(file => { files[file.path] = file; });
      activePath = Object.keys(files).sort().find(path => path === 'main.py') || Object.keys(files).sort()[0];
      editor.setValue(files[activePath] ? files[activePath].content : '');
      document.getElementById('project-select').value = String(id);
      markDirty(false);
      renderFileTree();
      renderTabs();
    } catch (err) { PA.toast(err.message, 'error'); }
  }

  async function saveCurrent(showToast) {
    syncCurrent();
    if (!activePath || !files[activePath]) return;
    try {
      await PA.api(`/api/ide/files/${files[activePath].id}`, {
        method: 'PUT', body: { content: files[activePath].content }
      });
      markDirty(false);
      if (showToast) PA.toast('File saved.', 'success');
    } catch (err) { PA.toast(err.message, 'error'); }
  }

  async function saveAll() {
    syncCurrent();
    try {
      const payload = {};
      Object.entries(files).forEach(([path, file]) => { payload[path] = file.content; });
      const data = await PA.api(`/api/ide/projects/${project.id}/save`, { method: 'POST', body: { files: payload } });
      project = data.project;
      files = {};
      project.files.forEach(file => { files[file.path] = file; });
      markDirty(false);
      PA.toast('Project saved.', 'success');
      renderFileTree();
    } catch (err) { PA.toast(err.message, 'error'); }
  }

  async function run() {
    if (controller || !project) return;
    syncCurrent();
    const payload = { entrypoint: 'main.py', stdin: document.getElementById('stdin-input').value, files: {} };
    Object.entries(files).forEach(([path, file]) => { payload.files[path] = file.content; });
    if (!payload.files['main.py']) { PA.toast('Add a main.py file to run this project.', 'error'); return; }
    controller = new AbortController();
    document.getElementById('run-btn').disabled = true;
    document.getElementById('stop-btn').disabled = false;
    document.getElementById('console-output').textContent = 'Running…';
    try {
      const data = await PA.api('/api/execute', { method: 'POST', signal: controller.signal, body: payload });
      document.getElementById('console-output').innerHTML = data.stdout
        ? esc(data.stdout) : '<span class="empty-console">(no output)</span>';
      document.getElementById('console-errors').textContent = [data.error, data.stderr].filter(Boolean).join('\n') || 'No errors.';
    } catch (err) {
      document.getElementById('console-output').textContent = err.name === 'AbortError' ? 'Execution stopped.' : err.message;
    } finally {
      controller = null;
      document.getElementById('run-btn').disabled = false;
      document.getElementById('stop-btn').disabled = true;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    editor = PA.createEditor(document.getElementById('code-input'), {
      lineWrapping: false,
      onRun: run,
      onSave: saveAll,
      onChange: () => markDirty(true),
      onCursor: cm => {
        const pos = cm.getCursor();
        document.getElementById('status-cursor').textContent = `Ln ${pos.line + 1}, Col ${pos.ch + 1}`;
      }
    });
    loadProjects();

    document.getElementById('project-select').addEventListener('change', event => openProject(Number(event.target.value)));
    document.getElementById('save-btn').addEventListener('click', saveAll);
    document.getElementById('run-btn').addEventListener('click', run);
    document.getElementById('stop-btn').addEventListener('click', () => controller && controller.abort());
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
    document.querySelectorAll('[data-ide-view]').forEach(button => button.addEventListener('click', () => {
      const console = document.querySelector('.ide-editor .console');
      const host = document.querySelector('.ide-editor .editor-host');
      const tabs = document.getElementById('editor-tabs');
      const showConsole = button.dataset.ideView === 'console';
      console.style.display = showConsole ? 'block' : 'none';
      host.style.display = showConsole ? 'none' : 'block';
      tabs.style.display = showConsole ? 'none' : 'flex';
      if (!showConsole) editor.refresh();
      document.querySelectorAll('[data-ide-view]').forEach(b => b.classList.toggle('btn-primary', b === button));
    }));

    document.getElementById('new-project').addEventListener('click', async () => {
      const name = prompt('Project name:');
      if (!name) return;
      try {
        const data = await PA.api('/api/ide/projects', { method: 'POST', body: { name } });
        projects.push(data.project);
        const select = document.getElementById('project-select');
        select.innerHTML = projects.map(p => `<option value="${p.id}">${esc(p.name)}</option>`).join('');
        await openProject(data.project.id);
        PA.toast('Project created.', 'success');
      } catch (err) { PA.toast(err.message, 'error'); }
    });
    document.getElementById('rename-project').addEventListener('click', async () => {
      if (!project) return;
      const name = prompt('New project name:', project.name);
      if (!name) return;
      try {
        await PA.api(`/api/ide/projects/${project.id}`, { method: 'PATCH', body: { name } });
        project.name = name;
        const option = document.querySelector(`#project-select option[value="${project.id}"]`);
        if (option) option.textContent = name;
        renderFileTree();
      } catch (err) { PA.toast(err.message, 'error'); }
    });
    document.getElementById('delete-project').addEventListener('click', async () => {
      if (!project || !confirm(`Delete project "${project.name}" and all its files?`)) return;
      try {
        await PA.api(`/api/ide/projects/${project.id}`, { method: 'DELETE' });
        projects = projects.filter(p => p.id !== project.id);
        if (projects.length) {
          document.getElementById('project-select').innerHTML = projects.map(p => `<option value="${p.id}">${esc(p.name)}</option>`).join('');
          await openProject(projects[0].id);
        } else { await loadProjects(); }
        PA.toast('Project deleted.');
      } catch (err) { PA.toast(err.message, 'error'); }
    });
    document.getElementById('new-file').addEventListener('click', async () => {
      if (!project) return;
      const path = prompt('File path (e.g. utils/helpers.py):');
      if (!path) return;
      try {
        const data = await PA.api(`/api/ide/projects/${project.id}/files`, { method: 'POST', body: { path, content: '' } });
        files[data.file.path] = data.file;
        openFile(data.file.path);
        PA.toast('File created.', 'success');
      } catch (err) { PA.toast(err.message, 'error'); }
    });
    document.getElementById('delete-file').addEventListener('click', async () => {
      if (!activePath || !files[activePath] || !confirm(`Delete ${activePath}?`)) return;
      try {
        await PA.api(`/api/ide/files/${files[activePath].id}`, { method: 'DELETE' });
        delete files[activePath];
        activePath = Object.keys(files).sort()[0];
        editor.setValue(activePath ? files[activePath].content : '');
        renderFileTree(); renderTabs();
        PA.toast('File deleted.');
      } catch (err) { PA.toast(err.message, 'error'); }
    });
    document.getElementById('format-btn').addEventListener('click', async () => {
      try {
        const data = await PA.api('/api/format', { method: 'POST', body: { code: editor.getValue() } });
        editor.setValue(data.code);
        PA.toast('File formatted with Black.', 'success');
      } catch (err) { PA.toast(err.message, 'error'); }
    });
    window.addEventListener('beforeunload', event => {
      if (dirty) { event.preventDefault(); event.returnValue = ''; }
    });
  });
})();

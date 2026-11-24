(function () {
  'use strict';
  const esc = PA.escapeHtml;
  const root = document.getElementById('workspace-root');
  const type = root.dataset.itemType;
  const slug = root.dataset.itemSlug;
  let editor = null;
  let starter = '';
  let controller = null;

  const endpoint = type === 'project' ? `/api/projects/${slug}`
    : type === 'challenge' ? `/api/challenges/${slug}` : `/api/exercises/${slug}`;

  function list(items) {
    return (items || []).map(item => `<li>${esc(item)}</li>`).join('');
  }

  function brief(data) {
    if (type === 'project') {
      const p = data.project;
      const steps = (p.steps || []).map((step, i) =>
        `<li><strong>${esc(step.title)}</strong>${esc(step.detail)}
           ${step.hint ? `<button class="hint-button" data-hint="${i}">Show hint</button><div class="hint">${esc(step.hint)}</div>` : ''}</li>`).join('');
      return `<p>${esc(p.intro)}</p>
        <h3>What you'll learn</h3><ul class="check-list">${list(p.outcomes)}</ul>
        <h3>Concepts you'll use</h3><div class="chip-row">${(p.concepts || []).map(c => `<span class="chip">${esc(c)}</span>`).join('')}</div>
        <h3>Objectives</h3><ul class="check-list">${list(p.objectives)}</ul>
        <h3>Steps</h3><ol class="steps">${steps}</ol>
        <h3>Requirements &amp; expected behaviour</h3><ul class="check-list">${list(p.requirements)}</ul>
        ${data.status === 'completed' ? `<h3>Concepts you demonstrated</h3><p>${esc(p.completion_summary)}</p>` : ''}
        <h3>Useful topics</h3><div class="topic-list">${(data.related_topics || []).map(t => `<a class="topic-chip" href="/library/${t.slug}">📘 ${esc(t.title)}</a>`).join('')}</div>`;
    }
    if (type === 'challenge') {
      const c = data.challenge;
      return `<p>${esc(c.description)}</p>
        <div class="chip-row"><span class="badge yellow">Difficulty ${c.difficulty}/5</span><span class="badge blue">${esc(c.category)}</span><span class="badge green">${c.points} points</span></div>
        <h3>Required signature</h3><pre class="mono small" style="background:var(--bg);padding:10px;border-radius:8px;overflow:auto">${esc(c.starter_code.split('\n')[0])}</pre>
        <h3>Input</h3><p class="small">${esc(c.input_spec)}</p>
        <h3>Output</h3><p class="small">${esc(c.output_spec)}</p>
        <h3>Example tests</h3><div class="test-results">${(c.examples || []).map(e => `<div class="test-row"><span class="icon muted">→</span><div><span class="mono">${esc(e.input)}</span><br><span class="muted">returns</span> <span class="mono text-green">${esc(e.output)}</span></div></div>`).join('')}</div>
        <h3>Concepts</h3><p class="small">${esc(c.concept_explanation)}</p>
        <h3>Hints</h3>${(c.hints || []).map((h, i) => `<button class="hint-button" data-hint="${i}">Show hint ${i + 1}</button><div class="hint">${esc(h)}</div>`).join('')}`;
    }
    const e = data.exercise;
    return `<p>${esc(e.prompt)}</p><p class="small muted">Topic: <a href="/library/${e.topic.slug}">${esc(e.topic.title)}</a></p>
      <h3>Your task</h3><p class="small">Implement the function in the editor so all tests pass. Use the Output tab to experiment and the Test results tab after submitting.</p>`;
  }

  function setConsole(tab) {
    ['output', 'errors', 'tests'].forEach(name => {
      document.getElementById('console-' + name).style.display = name === tab ? 'block' : 'none';
      document.querySelector(`[data-console-tab="${name}"]`)?.classList.toggle('active', name === tab);
    });
  }

  function renderResults(result) {
    const clean = result.results || [];
    document.getElementById('console-tests').innerHTML =
      `<div style="display:flex;gap:10px;align-items:center;margin-bottom:10px">
         <span class="badge ${result.passed === result.total ? 'green' : 'red'}">${result.passed}/${result.total} tests passed</span>
         <span class="muted small">${result.duration_ms || 0} ms</span></div>
       <div class="test-results">${clean.map(t => `<div class="test-row ${t.passed ? 'pass' : 'fail'}">
         <span class="icon ${t.passed ? 'text-green' : 'text-red'}">${t.passed ? '✓' : '✕'}</span>
         <div><strong>${esc(t.name)}</strong>${t.hidden && !t.passed ? '<div class="muted tiny">Hidden test — details withheld</div>' : ''}
         ${!t.passed && t.error ? `<pre>${esc(t.error)}</pre>` : ''}</div></div>`).join('')}</div>`;
    setConsole('tests');
  }

  async function runCode() {
    if (controller) return;
    controller = new AbortController();
    document.getElementById('run-btn').disabled = true;
    document.getElementById('stop-btn').disabled = false;
    const output = document.getElementById('console-output');
    output.textContent = 'Running…';
    setConsole('output');
    try {
      const data = await PA.api('/api/execute', { method: 'POST', signal: controller.signal, body: {
        code: editor.getValue(), stdin: document.getElementById('stdin-input').value
      }});
      output.innerHTML = (data.stdout ? esc(data.stdout) : '<span class="empty-console">(no output)</span>')
        + (data.truncated ? '\n\n⚠ Output was truncated.' : '');
      const err = document.getElementById('console-errors');
      err.textContent = [data.error, data.stderr].filter(Boolean).join('\n') || 'No errors.';
      if (data.error || data.stderr) document.querySelector('[data-console-tab="errors"]').classList.add('active');
    } catch (err) {
      if (err.name === 'AbortError') output.textContent = 'Execution stopped.';
      else { output.textContent = err.message; PA.toast(err.message, 'error'); }
    } finally {
      controller = null;
      document.getElementById('run-btn').disabled = false;
      document.getElementById('stop-btn').disabled = true;
    }
  }

  async function submit() {
    const button = document.getElementById('submit-btn');
    button.disabled = true;
    button.textContent = 'Checking…';
    document.getElementById('console-tests').textContent = 'Running the test suite in the sandbox…';
    setConsole('tests');
    try {
      const data = await PA.api('/api/submit', { method: 'POST', body: {
        item_type: type, slug, code: editor.getValue()
      }});
      renderResults(data.result);
      document.getElementById('workspace-status').textContent = `${data.passed}/${data.total} tests · ${data.score || (data.submission ? data.submission.score : 0)}%`;
      if (data.completed) {
        document.getElementById('workspace-status').className = 'badge green';
        PA.toast('All tests passed. Project progress saved!', 'success');
        if (type === 'project') document.getElementById('brief-content').innerHTML = brief(data.project || { project: {} });
      } else {
        document.getElementById('workspace-status').className = 'badge yellow';
        PA.toast(`${data.passed} of ${data.total} tests passed — keep going.`, 'error');
      }
      (data.achievements_unlocked || []).forEach(code => PA.toast(`Achievement unlocked: ${code}`, 'success'));
    } catch (err) {
      document.getElementById('console-tests').textContent = err.message;
      PA.toast(err.message, 'error');
    } finally {
      button.disabled = false;
      button.textContent = 'Submit solution';
    }
  }

  document.addEventListener('DOMContentLoaded', async () => {
    try {
      const data = await PA.api(endpoint);
      const item = data.project || data.challenge || data.exercise;
      document.getElementById('brief-title').textContent = type === 'challenge' ? 'Challenge' : type === 'exercise' ? 'Practice exercise' : 'Project brief';
      document.getElementById('brief-content').innerHTML = brief(data);
      starter = (data.last_code && data.last_code.trim()) ? data.last_code : (item.starter_code || '');
      editor = PA.createEditor(document.getElementById('code-input'), {
        height: '420px', lineWrapping: true, onRun: runCode,
        onSave: () => PA.toast('Tip: use the Save button in the IDE to store multi-file projects.', '')
      });
      editor.setValue(starter);
      document.getElementById('workspace-subtitle').textContent =
        `Level ${item.level} · ${type === 'project' ? 'Project' : type === 'challenge' ? 'Challenge' : 'Exercise'} · ${item.estimated_minutes || 'self-paced'} min`;
      if (data.status === 'completed') {
        document.getElementById('workspace-status').textContent = 'Completed ✓';
        document.getElementById('workspace-status').className = 'badge green';
      } else {
        document.getElementById('workspace-status').textContent = data.status === 'in_progress' ? 'In progress' : 'Not started';
      }
      document.querySelectorAll('[data-hint]').forEach(button => {
        button.addEventListener('click', () => {
          const hint = button.nextElementSibling;
          if (hint) { hint.style.display = hint.style.display === 'block' ? 'none' : 'block'; }
        });
      });
    } catch (err) { PA.toast(err.message, 'error'); }

    document.getElementById('run-btn').addEventListener('click', runCode);
    document.getElementById('submit-btn').addEventListener('click', submit);
    document.getElementById('stop-btn').addEventListener('click', () => controller && controller.abort());
    document.getElementById('reset-btn').addEventListener('click', () => {
      if (confirm('Replace your code with the starter code?')) editor.setValue(starter);
    });
    document.getElementById('clear-btn').addEventListener('click', () => {
      ['output', 'errors', 'tests'].forEach(name => {
        document.getElementById('console-' + name).innerHTML = '<span class="empty-console">Console cleared.</span>';
      });
    });
    document.getElementById('format-btn').addEventListener('click', async () => {
      try {
        const data = await PA.api('/api/format', { method: 'POST', body: { code: editor.getValue() } });
        editor.setValue(data.code);
        PA.toast('Code formatted with Black.', 'success');
      } catch (err) { PA.toast(err.message, 'error'); }
    });
    document.querySelectorAll('[data-console-tab]').forEach(button => {
      button.addEventListener('click', () => setConsole(button.dataset.consoleTab));
    });
    document.querySelectorAll('[data-mobile-tab]').forEach(button => {
      button.addEventListener('click', () => {
        const tab = button.dataset.mobileTab;
        document.getElementById('brief-panel').style.display = tab === 'brief' ? 'block' : 'none';
        document.getElementById('editor-panel').style.display = tab === 'console' ? 'none' : 'block';
        document.querySelector('.console').style.display = tab === 'console' ? 'block' : 'none';
        document.querySelectorAll('[data-mobile-tab]').forEach(b => b.classList.toggle('btn-primary', b === button));
      });
    });
  });
})();

(function () {
  'use strict';

  function message(id, text, type) {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = type === 'error' ? 'form-error' : 'form-success';
  }

  async function load() {
    try {
      const { user } = await PA.api('/api/me');
      document.getElementById('username').value = user.username;
      document.getElementById('email').value = user.email;
      document.getElementById('created-at').textContent = (user.created_at || '').slice(0, 10);
      document.getElementById('account-level').textContent = user.current_level;
      document.getElementById('theme').value = user.theme;
      document.getElementById('font-size').value = String(user.preferences.font_size);
      document.getElementById('tab-size').value = String(user.preferences.tab_size);
      document.getElementById('line-wrapping').checked = user.preferences.line_wrapping;
      document.getElementById('auto-hint').checked = user.preferences.auto_hint;
    } catch (err) { message('profile-error', err.message, 'error'); }
  }

  document.addEventListener('DOMContentLoaded', () => {
    load();
    document.getElementById('profile-form').addEventListener('submit', async event => {
      event.preventDefault();
      try {
        const { user } = await PA.api('/api/me', { method: 'PATCH', body: {
          username: document.getElementById('username').value.trim(),
          email: document.getElementById('email').value.trim()
        }});
        message('profile-success', 'Account details saved.', 'success');
        message('profile-error', '');
        document.querySelector('.avatar').textContent = user.username.slice(0, 1).toUpperCase();
        document.querySelector('.avatar').title = user.username;
      } catch (err) { message('profile-error', err.message, 'error'); }
    });

    document.getElementById('prefs-form').addEventListener('submit', async event => {
      event.preventDefault();
      const theme = document.getElementById('theme').value;
      try {
        await PA.api('/api/me/preferences', { method: 'PATCH', body: {
          theme,
          font_size: Number(document.getElementById('font-size').value),
          tab_size: Number(document.getElementById('tab-size').value),
          line_wrapping: document.getElementById('line-wrapping').checked,
          auto_hint: document.getElementById('auto-hint').checked
        }});
        document.documentElement.dataset.theme = theme;
        document.body.dataset.fontSize = document.getElementById('font-size').value;
        document.body.dataset.tabSize = document.getElementById('tab-size').value;
        document.body.dataset.lineWrap = document.getElementById('line-wrapping').checked ? '1' : '0';
        message('prefs-success', 'Preferences saved. They will apply to editors opened from now on.', 'success');
        message('prefs-error', '');
      } catch (err) { message('prefs-error', err.message, 'error'); }
    });

    document.getElementById('password-form').addEventListener('submit', async event => {
      event.preventDefault();
      try {
        await PA.api('/api/me/password', { method: 'POST', body: {
          current_password: document.getElementById('current-password').value,
          new_password: document.getElementById('new-password').value
        }});
        document.getElementById('password-form').reset();
        message('password-success', 'Password updated.', 'success');
        message('password-error', '');
      } catch (err) { message('password-error', err.message, 'error'); }
    });
  });
})();

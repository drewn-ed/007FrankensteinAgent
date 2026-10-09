export async function mountChatGPTSettings(node, {api, esc, toast, refresh, state}) {
  let selectedState = state;
  try {
    const connection = await api('/api/chatgpt/status');
    const active = connection.profiles.find(p => p.id === connection.active);
    node.innerHTML = `<div class="settings-section-heading"><h3>Model connection</h3><p>Choose the model that handles your tasks.</p></div>
      <div class="model-connection">
        <div class="model-connection-heading"><strong>ChatGPT plan</strong><span class="connection-status ${connection.connected ? 'is-connected' : ''}">${connection.connected ? 'Connected' : 'Not connected'}</span></div>
        <p class="connection-account">${connection.connected ? esc(active?.email || 'ChatGPT account') : 'Sign in to use your ChatGPT subscription.'}</p>
        <p id="chatgpt-activation-status" class="connection-hint">${connection.connected && state.provider !== 'chatgpt' ? `Currently using ${esc(state.provider_label || 'Gemini')}. Choose a model below to switch.` : ''}</p>
        ${connection.connected ? '' : '<button class="primary-button connect-plan" id="chatgpt-connect">Continue with ChatGPT</button>'}
        <div id="chatgpt-models"></div>
        <p id="chatgpt-message" class="settings-message" role="status"></p>
        ${connection.connected ? `<div class="connection-footer"><span>Uses your ChatGPT plan</span><a href="https://chatgpt.com/settings/usage" target="_blank" rel="noopener noreferrer">Usage &amp; limits</a></div>
        <details class="account-options"><summary>Account options</summary><div class="account-actions"><button class="quiet-button" id="chatgpt-connect">Reconnect account</button><button class="quiet-button" id="chatgpt-add">Add another account</button></div><p>Manage this app’s plan and credit access in ChatGPT. No automatic API fallback.</p></details>` : ''}
      </div>`;
    const message = node.querySelector('#chatgpt-message');
    async function connect(profileId) {
      try {
        message.textContent = 'Opening secure ChatGPT sign-in…';
        const {url} = await api('/api/chatgpt/login', profileId ? {profile_id: profileId} : {});
        window.location.assign(url);
      } catch (error) { message.textContent = error.message; }
    }
    node.querySelector('#chatgpt-connect').onclick = () => connect(connection.active);
    node.querySelector('#chatgpt-add')?.addEventListener('click', () => connect(null));
    if (connection.connected) {
      node.querySelector('#chatgpt-models').textContent = 'Loading available models…';
      try {
      const {models} = await api('/api/chatgpt/models');
      node.querySelector('#chatgpt-models').innerHTML = models.length ? `<div class="model-field"><label for="chatgpt-model">Model</label><select id="chatgpt-model" aria-describedby="chatgpt-selection-note">${models.map(m => `<option value="${esc(m.slug)}" ${state.provider === 'chatgpt' && state.model === m.slug ? 'selected' : ''}>${esc(m.display_name)}</option>`).join('')}</select></div><div class="model-selection-footer"><p id="chatgpt-selection-note"></p><button class="primary-button" id="chatgpt-use">Use selected model</button></div>` : '<p>No eligible models were returned for this account.</p>';
      function updateSelection() {
        const button = node.querySelector('#chatgpt-use');
        if (!button) return;
        const isActive = selectedState.provider === 'chatgpt' && selectedState.model === node.querySelector('#chatgpt-model').value;
        button.disabled = isActive;
        button.hidden = isActive;
        button.textContent = 'Use selected model';
        const note = node.querySelector('#chatgpt-selection-note');
        note.textContent = isActive ? 'In use · Ready for your next task' : 'Applies to new tasks.';
        note.classList.toggle('is-current', isActive);
      }
      node.querySelector('#chatgpt-model')?.addEventListener('change', updateSelection);
      updateSelection();
      node.querySelector('#chatgpt-use')?.addEventListener('click', async () => {
        const button = node.querySelector('#chatgpt-use');
        const picker = node.querySelector('#chatgpt-model');
        button.disabled = true;
        picker.disabled = true;
        button.textContent = 'Switching…';
        message.textContent = 'Activating model…';
        try {
          selectedState = await api('/api/chatgpt/activate', {model: picker.value});
          await refresh();
          node.querySelector('#chatgpt-activation-status').textContent = '';
          message.textContent = 'Model updated. Your next task will use this selection.';
          toast('ChatGPT model configured.');
        } catch (error) { message.textContent = error.message; }
        finally { picker.disabled = false; updateSelection(); }
      });
      } catch (error) {
        node.querySelector('#chatgpt-models').textContent = 'Could not load models. Your account remains connected.';
        message.textContent = error.message;
      }
    }
  } catch (error) { node.textContent = error.message; }
}

(() => {
  const root = document.documentElement;
  const key = 'learning-workspace-theme';
  let saved;
  try { saved = localStorage.getItem(key); } catch { /* Storage is optional. */ }
  root.dataset.dsTheme = saved === 'dark' ? 'dark' : 'light';

  document.addEventListener('DOMContentLoaded', () => {
    const button = document.getElementById('theme-toggle');
    const updateLabel = () => {
      const next = root.dataset.dsTheme === 'dark' ? 'light' : 'dark';
      button.textContent = `${next === 'dark' ? 'Dark' : 'Light'} mode`;
      button.setAttribute('aria-label', `Switch to ${next} theme`);
    };
    updateLabel();
    button.hidden = false;
    button.addEventListener('click', () => {
      root.dataset.dsTheme = root.dataset.dsTheme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(key, root.dataset.dsTheme); } catch { /* Continue without persistence. */ }
      updateLabel();
    });
  });
})();

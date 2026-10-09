// A reading preference supplements the default division between display and UI text.
(() => {
  const button = document.getElementById('plain-type');
  const apply = plain => {
    document.documentElement.dataset.dsType = plain ? 'plain' : 'brand';
    button.setAttribute('aria-pressed', String(plain));
  };
  try { apply(localStorage.getItem('ds-plain-type') === 'true'); } catch {}
  button.addEventListener('click', () => {
    const plain = button.getAttribute('aria-pressed') !== 'true';
    apply(plain);
    try { localStorage.setItem('ds-plain-type', String(plain)); } catch {}
  });
})();

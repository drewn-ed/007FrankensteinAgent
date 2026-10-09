// A small motion layer: routing and task state stay in the application.
export function createInteractions() {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const nav = document.querySelector('.primary-nav');
  const bubble = document.createElement('span');
  bubble.className = 'nav-bubble';
  bubble.setAttribute('aria-hidden', 'true');
  bubble.hidden = true;
  nav.prepend(bubble);
  let navFrame, viewFrame, destination, navAnimation, viewAnimation;

  function placeBubble() {
    const active = nav.querySelector('.nav-row.active');
    const navRect = nav.getBoundingClientRect();
    if (!active || !navRect.width || !navRect.height) {
      navAnimation?.cancel();
      bubble.hidden = true;
      nav.classList.remove('has-nav-bubble');
      destination = null;
      return;
    }
    // Layout coordinates ignore the button's brief press transform.
    const next = { x: active.offsetLeft, y: active.offsetTop, width: active.offsetWidth, height: active.offsetHeight };
    if (destination && Object.keys(next).every(key => next[key] === destination[key])) return;
    // Read the in-flight position before cancelling, so quick clicks never jump.
    const current = bubble.hidden ? null : bubble.getBoundingClientRect();
    navAnimation?.cancel();
    bubble.style.width = `${next.width}px`;
    bubble.style.height = `${next.height}px`;
    bubble.style.transform = `translate(${next.x}px, ${next.y}px)`;
    bubble.hidden = false;
    nav.classList.add('has-nav-bubble');
    if (current && !reduced.matches) {
      const x = current.left - navRect.left, y = current.top - navRect.top;
      navAnimation = bubble.animate([
        { transform: `translate(${x}px, ${y}px)` },
        { transform: `translate(${next.x}px, ${next.y}px)` },
      ], { duration: 400, easing: 'cubic-bezier(.22, 1, .36, 1)' });
    }
    destination = next;
  }

  function syncNavigation() {
    for (const item of document.querySelectorAll('.sidebar .nav-row, .sidebar .chat-link')) {
      if (item.classList.contains('active')) item.setAttribute('aria-current', 'page');
      else item.removeAttribute('aria-current');
    }
    cancelAnimationFrame(navFrame);
    navFrame = requestAnimationFrame(placeBubble);
  }

  function enterView(view) {
    cancelAnimationFrame(viewFrame);
    viewAnimation?.cancel();
    if (reduced.matches) return;
    viewFrame = requestAnimationFrame(() => {
      viewAnimation = view.animate([
        { opacity: .35, transform: 'translateY(8px)' },
        { opacity: 1, transform: 'translateY(0)' },
      ], { duration: 200, easing: 'cubic-bezier(.22, 1, .36, 1)' });
    });
  }

  // Delegation covers controls created by library, inspector and settings renders.
  document.addEventListener('click', event => {
    const button = event.target.closest('button');
    if (!button || button.disabled || button.getAttribute('aria-disabled') === 'true' ||
        reduced.matches || button.matches('.sidebar-shade, .primary-nav .nav-row')) return;
    button.querySelector(':scope > .button-ripple')?.remove();
    const rect = button.getBoundingClientRect();
    const x = event.detail ? event.clientX - rect.left : rect.width / 2;
    const y = event.detail ? event.clientY - rect.top : rect.height / 2;
    const size = Math.hypot(Math.max(x, rect.width - x), Math.max(y, rect.height - y)) * 2;
    const ripple = document.createElement('span');
    ripple.className = 'button-ripple';
    ripple.setAttribute('aria-hidden', 'true');
    const ink = document.createElement('span');
    ink.style.cssText = `width:${size}px;height:${size}px;left:${x - size / 2}px;top:${y - size / 2}px`;
    ripple.append(ink);
    button.append(ripple);
    ink.addEventListener('animationend', () => ripple.remove(), { once: true });
    // Also clean up if reduced motion is enabled while the ripple is running.
    setTimeout(() => ripple.remove(), 450);
  }, true);

  const resize = new ResizeObserver(syncNavigation);
  resize.observe(nav);
  for (const row of nav.querySelectorAll('.nav-row')) resize.observe(row);
  document.fonts.ready.then(syncNavigation);
  reduced.addEventListener('change', () => {
    navAnimation?.cancel();
    viewAnimation?.cancel();
    cancelAnimationFrame(viewFrame);
    document.querySelectorAll('.button-ripple').forEach(ripple => ripple.remove());
    syncNavigation();
  });
  syncNavigation();
  return { syncNavigation, enterView };
}

// Only show pending feedback while an actual operation is in flight.
export async function withButtonFeedback(button, label, action) {
  if (button.disabled) return;
  const original = [...button.childNodes];
  const previousLabel = button.getAttribute('aria-label');
  const previousBusy = button.getAttribute('aria-busy');
  const loader = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  loader.classList.add('icon', 'button-loader');
  loader.setAttribute('aria-hidden', 'true');
  const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
  use.setAttribute('href', `${document.getElementById('nucleo-loader') ? '' : '/design/icons/nucleo-pixel/sprite.svg'}#nucleo-loader`);
  loader.append(use);
  const caption = document.createElement('span');
  caption.textContent = label;
  if (button.classList.contains('icon-button')) caption.className = 'sr-only';
  button.disabled = true;
  button.setAttribute('aria-busy', 'true');
  button.setAttribute('aria-label', label);
  button.replaceChildren(loader, caption);
  try {
    return await action();
  } finally {
    button.replaceChildren(...original.filter(node => !node.classList?.contains('button-ripple')));
    button.disabled = false;
    if (previousLabel === null) button.removeAttribute('aria-label');
    else button.setAttribute('aria-label', previousLabel);
    if (previousBusy === null) button.removeAttribute('aria-busy');
    else button.setAttribute('aria-busy', previousBusy);
  }
}

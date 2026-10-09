const rendered = new WeakMap();

// Refresh live data without resetting the user's expanded sections or reading position.
export function updateLivePanel(container, html) {
  if (rendered.get(container) === html) return;
  const disclosures = new Map([...container.querySelectorAll('details[data-disclosure]')]
    .map(detail => [detail.dataset.disclosure, detail.open]));
  const focused = container.contains(document.activeElement) && document.activeElement.matches('summary')
    ? document.activeElement.parentElement.dataset.disclosure : null;
  const scroll = [];
  for (let parent = container; parent; parent = parent.parentElement) {
    if (parent.scrollTop || parent.scrollLeft) scroll.push([parent, parent.scrollTop, parent.scrollLeft]);
  }
  const template = document.createElement('template');
  template.innerHTML = html;
  let focusTarget;
  for (const detail of template.content.querySelectorAll('details[data-disclosure]')) {
    const key = detail.dataset.disclosure;
    if (disclosures.has(key)) detail.open = disclosures.get(key);
    if (key === focused) focusTarget = detail.querySelector('summary');
  }
  // Set open before insertion: a briefly collapsed map would clamp the scroll position.
  container.replaceChildren(template.content);
  rendered.set(container, html);
  focusTarget?.focus({ preventScroll: true });
  for (const [parent, top, left] of scroll) {
    parent.scrollTop = top;
    parent.scrollLeft = left;
  }
}

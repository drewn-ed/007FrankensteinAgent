"""Generate framework-independent CSS from tokens.json. Python standard library only."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "tokens.json").read_text())
out = ["/* Generated from tokens.json. Run: python3 design/build_tokens.py */"]
for face in data["fontFaces"]:
    out += [f"""@font-face {{
  font-family: '{face['family']}'; src: url('./fonts/{face['file']}') format('{"woff2" if face["file"].endswith(".woff2") else "truetype"}');
  font-style: normal; font-weight: {face['weight']}; font-display: swap;
}}"""]
out += [":root {"]
for key, val in data["font"].items():
    out += [f"  --ds-font-{key}: {val};"]
for key, val in data["palette"].items():
    out += [f"  --ds-palette-{key}: {val};"]
for group in ["space", "radius"]:
    for key, val in data[group].items():
        out += [f"  --ds-{group}-{key}: {val / 16:g}rem;"]
for key, val in data["motion"].items():
    out += [f"  --ds-motion-{key}: {val}{'ms' if isinstance(val, int) else ''};"]
for key in ("size", "large", "stroke"):
    out += [f"  --ds-icon-{key}: {data['icons'][key]}px;"]
out += ["}"]
for theme, values in data["themes"].items():
    selector = ':root, [data-ds-theme="light"]' if theme == "light" else '[data-ds-theme="dark"]'
    out += [selector + " {", f"  color-scheme: {theme};"]
    out += [f"  --ds-{key}: {val};" for key, val in values.items()]
    out += ["}"]
out += ['[data-ds-type="plain"] { --ds-font-display: var(--ds-font-text); }']
out += [".ds-root { font-family: var(--ds-font-text); color: var(--ds-text); background: var(--ds-canvas); font-synthesis: none; }"]
for role, val in data["type"].items():
    out += [f".ds-type-{role} {{ font-family: var(--ds-font-{val['family']}); font-size: {val['size']/16:g}rem; line-height: {val['line']/val['size']:.5f}; font-weight: {val['weight']}; letter-spacing: {val['tracking']}; }}"]
out += [""".ds-numbers { font-variant-numeric: tabular-nums; }
.ds-icon { width: var(--ds-icon-size); height: var(--ds-icon-size); display: inline-block; flex: none; vertical-align: middle; color: inherit; }
.ds-icon--large { width: var(--ds-icon-large); height: var(--ds-icon-large); }
.ds-button {
  display: inline-flex; align-items: center; justify-content: center; gap: var(--ds-space-2);
  min-height: 44px; padding: 10px 18px; border: 1px solid transparent;
  border-radius: var(--ds-radius-control); font: 600 1rem/1.5 var(--ds-font-text);
  background: var(--ds-accent); color: var(--ds-on-accent); text-decoration: none;
  cursor: pointer; transition: background var(--ds-motion-fast) ease;
}
.ds-button:hover { background: var(--ds-accent-hover); }
.ds-button--secondary { background: var(--ds-surface); color: var(--ds-text); border-color: var(--ds-border-control); }
.ds-button--secondary:hover { background: var(--ds-surface-alt); }
.ds-button:disabled { cursor: not-allowed; opacity: 0.45; }
.ds-button:focus-visible, .ds-input:focus-visible, .ds-link:focus-visible {
  outline: 3px solid var(--ds-focus); outline-offset: 3px;
}
.ds-input { width: 100%; padding: 12px 14px; border: 1px solid var(--ds-border-control); border-radius: var(--ds-radius-control); background: var(--ds-surface); color: var(--ds-text); font: 400 1rem/1.5 var(--ds-font-text); }
.ds-input::placeholder { color: var(--ds-text-muted); opacity: 1; }
.ds-link { color: var(--ds-accent-text); text-decoration: underline; text-underline-offset: 0.2em; }
.ds-status { display: inline-flex; align-items: center; gap: 6px; padding: 4px 8px; border-radius: var(--ds-radius-small); font: 500 0.875rem/1.5 var(--ds-font-text); }
.ds-status--success { color: var(--ds-success); background: var(--ds-success-soft); }
.ds-status--warning { color: var(--ds-warning); background: var(--ds-warning-soft); }
.ds-status--danger { color: var(--ds-danger); background: var(--ds-danger-soft); }
.ds-status--info { color: var(--ds-info); background: var(--ds-info-soft); }
@media (prefers-reduced-motion: reduce) {
  :root { --ds-motion-fast: 0ms; --ds-motion-standard: 0ms; --ds-motion-expressive: 0ms; --ds-motion-stagger: 0ms; }
  .ds-button { transition: none; }
}
"""]
(ROOT / "tokens.css").write_text("\n".join(out))
print("Generated design/tokens.css")

# Keep the running prototype on the same source tokens and original font assets.
import shutil
web = ROOT.parent / 'web'
(web / 'fonts').mkdir(exist_ok=True)
(web / 'design-tokens.css').write_text('\n'.join(out))
for face in data['fontFaces']:
    shutil.copy2(ROOT / 'fonts' / face['file'], web / 'fonts' / face['file'])
for name in data['fontLicenses']:
    shutil.copy2(ROOT / 'fonts' / name, web / 'fonts' / name)
web_files = {face['file'] for face in data['fontFaces']} | set(data['fontLicenses'])
web_sources = [item for item in json.loads((ROOT / 'fonts' / 'sources.json').read_text()) if item['file'] in web_files]
(web / 'fonts' / 'sources.json').write_text(json.dumps(web_sources, indent=2) + '\n')
print('Synced prototype design tokens and web fonts')

import { cp, mkdir, rm } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../../', import.meta.url));
const output = path.join(root, 'dist');
await rm(output, { recursive: true, force: true });
await mkdir(path.join(output, 'assets'), { recursive: true });
for (const file of ['index.html', 'style.css', 'theme.js']) {
  await cp(path.join(root, 'landing', file), path.join(output, file));
}
// Explicit asset list: private project data and source docs are never deployed.
const assets = {
  'output/landing-hero-study/assets/tokens.css': 'assets/tokens.css',
  'output/landing-hero-study/assets/fonts': 'assets/fonts',
  'design/logo/pixel-ghost.svg': 'assets/pixel-ghost.svg',
  'design/landing/ghost-background-light-v2.png': 'assets/ghost-background-light.png',
  'design/landing/ghost-background-dark-v2.png': 'assets/ghost-background-dark.png',
};
for (const [source, target] of Object.entries(assets)) {
  await cp(path.join(root, source), path.join(output, target), { recursive: true });
}
console.log('Landing page built in dist/ from the Git-tracked design assets.');

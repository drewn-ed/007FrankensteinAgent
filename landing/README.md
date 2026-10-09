# Learning workspace landing page

First landing-page draft for David's Agents 0.0.7 project, October 9, 2026. The product name remains undecided; “Learning workspace” is a descriptive placeholder.

The editable, buildless site is in `dist/index.html` and `dist/style.css`. Serve `dist` with any static HTTP server. No installation, JavaScript runtime or API key is needed in the browser.

## Content and visual sources

- Copy follows the product blueprint and submission draft in the parent project's `docs/`. The page identifies the product as an experimental prototype and describes composition in a fresh session as a goal, not a verified result.
- `dist/assets/tokens.css` and `dist/assets/fonts/` are copies of the approved `design/` tokens and local fonts. Do not edit generated tokens here; refresh from the visual system when it changes. Font licenses and provenance are included.
- `dist/assets/pixel-ghost.svg` is David's approved project logo.
- `dist/assets/ghost-background.png` is the existing ImageGen background from `design/landing/ghost-background-v1.png`; it is decorative. The original remains unchanged.
- No third-party icon library is used by this page.

The main action scrolls to the learning-loop explanation. The project link opens the existing public reference repository, which is not represented as the final implementation or submission.

## Initial verification

- Local assets, stylesheet font references and anchor targets resolve.
- Local browser review at desktop, 390 px and 320 px: no horizontal overflow, images load, heading/body font families match the manual.
- Main action navigates to the learning-loop section. No browser console errors or warnings observed.
- Reduced motion disables smooth scrolling and hover transitions.

This checks the landing page only. It does not validate the learning agent's capabilities or establish a full accessibility audit.

# Wisp landing page

First landing-page draft for David's Agents 0.0.7 project, October 9, 2026. David confirmed the name **Wisp** on October 9, 2026; it replaces the earlier “Learning workspace” placeholder.

The editable, buildless site is in `dist/index.html` and `dist/style.css`. Serve `dist` with any static HTTP server. No installation, JavaScript runtime or API key is needed in the browser.

## Content and visual sources

- Copy follows the product blueprint and submission draft in the parent project's `docs/`. The page identifies the product as an experimental prototype and describes composition in a fresh session as a goal, not a verified result.
- `dist/assets/tokens.css` and `dist/assets/fonts/` are copies of the approved `design/` tokens and local fonts. Do not edit generated tokens here; refresh from the visual system when it changes. Font licenses and provenance are included.
- `dist/assets/pixel-ghost.svg` is David's approved project logo.
- `dist/assets/ghost-background.png` is the existing ImageGen background from `design/landing/ghost-background-v1.png`; it is decorative. The original remains unchanged.
- No third-party icon library is used by this page.

The main action scrolls to the learning-loop explanation. The project link opens the current public repository. David renamed it to `drewn-ed/Wisp` on October 9, 2026. The landing page is a product presentation, not evidence of an HQ submission.

## Initial verification

- Local assets, stylesheet font references and anchor targets resolve.
- Local browser review at desktop, 390 px and 320 px: no horizontal overflow, images load, heading/body font families match the manual.
- Main action navigates to the learning-loop section. No browser console errors or warnings observed.
- Reduced motion disables smooth scrolling and hover transitions.

This checks the landing page only. It does not validate the learning agent's capabilities or establish a full accessibility audit.

## Vercel deployment

The production Vercel project `wisp-landing` serves `landing/dist` from the `main` branch of `drewn-ed/Wisp`. Set Root Directory to `landing`; the included `vercel.json` selects a static deployment without dependency installation or build commands. The light/dark page, saved theme preference, Wisp wordmark and v2 hero backgrounds come from the reviewed landing-page branch (`bff5213`). No backend or environment variables are required.

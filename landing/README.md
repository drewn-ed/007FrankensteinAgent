# Wisp landing page

Live site: [wisp-landing.vercel.app](https://wisp-landing.vercel.app/).

A short English introduction to Wisp, David's experimental learning workspace. The page presents the idea and links to the project; it does not run the agent.

## Editing and preview

Edit `dist/index.html`, `dist/style.css` and `dist/theme.js`. Serve this directory with `python3 -m http.server 4173 --directory landing/dist` from the repository root. There are no dependencies to install or build steps to run.

The page uses the approved Geist Pixel Square and IBM Plex Mono fonts, shared design tokens, pixel ghost logo and light/dark v2 backgrounds. Assets come from the reviewed landing-page branch (`bff5213`). Font licenses and provenance are included under `dist/assets/fonts/`. Keep text as HTML; the artwork is decorative. On mobile the artwork follows the text. Light is the default, and the theme choice is stored locally when browser storage is available.

## Vercel deployment

The Vercel project `wisp-landing` is connected to `drewn-ed/Wisp`, production branch `main`, Root Directory `landing`. The included `vercel.json` publishes only `dist`, with no installation or build command. No environment variables, API keys or backend are required.

Production commit `022feed` was verified on October 9, 2026: Vercel reported Ready, the public domain returned HTTP 200 without authentication, and the live page displayed Wisp with a working light/dark switch. Earlier ChatGPT Sites previews are separate, older versions.

Local browser checks also covered 1440, 390 and 320 px layouts, local assets, anchor navigation and theme persistence. These checks apply to the landing page, not the agent's runtime behavior or a full accessibility audit.

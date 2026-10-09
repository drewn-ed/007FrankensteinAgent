# Wisp landing-page hero: image and typography previews

Start here to review the opening screen or hand the assets to another agent. These are visual studies for Wisp with proposed English copy, not the final landing page. Existing screenshots predate the naming decision; the editable HTML uses Wisp.

## Preview gallery

### Refined light theme

![Light hero with actual project typography](hero-light.png)

### Refined dark theme

![Dark hero with actual project typography](hero-dark.png)

### Mobile and original comparison

- [Light mobile layout](hero-light-mobile.png)
- [Dark mobile layout](hero-dark-mobile.png)
- [Original background with the same type](hero-original.png)

## Open the interactive comparison

After cloning or downloading this branch, open [index.html](index.html) in a browser. Switch between Original, Refined light and Refined dark. GitHub shows HTML source; the screenshots above are viewable directly on GitHub. No build step or network connection is needed for the local preview.

The preview includes its own snapshot of the project [design tokens](assets/tokens.json), [CSS](assets/tokens.css) and fonts, so it does not depend on unpublished files from another working branch. Font files are unmodified and their licenses and provenance are included in [assets/fonts](assets/fonts).

## Assets for the landing-page implementation

- [Light background, no text](../../design/landing/ghost-background-light-v2.png)
- [Dark background, no text](../../design/landing/ghost-background-dark-v2.png)
- [Approved standalone logo](../../design/logo/pixel-ghost.svg)
- [Image prompts, design rationale and integration guidance](../../design/landing/README.md)

Use the background images behind real HTML text. Use Geist Pixel Square 400 for the headline and IBM Plex Mono for copy and controls. Preserve the calm text area on the left, and move the artwork below the text on mobile. The approved logo has no product name or wordmark. The preview headline and supporting copy are working copy, not confirmed marketing claims.

## Verification and optional rerendering

[Render checks](render-check.json) record the actual loaded fonts and preview widths. [Contrast checks](contrast-check.json) record this specific rendered composition; the background-only screenshots and measured text regions are kept alongside them.

The optional [render script](render.cjs) requires an existing Playwright setup and a compatible browser. Set `DESIGN_CHROME_PATH` if needed, otherwise it uses macOS Chrome when present or Playwright's default browser. Running it rewrites the local preview screenshots. Opening the HTML itself requires no developer tools.

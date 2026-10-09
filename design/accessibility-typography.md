# Pixel typography and accessibility

Research and design decision: October 9, 2026. This is implementation guidance, not a declaration of WCAG conformance or a legal assessment.

## Decision

Use **Geist Pixel Square 400** for short headings and brand moments, **IBM Plex Mono 400–700** for reading, controls, code and technical data. David selected Plex Mono for its fixed-width rhythm and technical character. The Square variant complements the Nucleo pixel icons without mixing different pixel textures. [Official font introduction](https://vercel.com/blog/introducing-geist-pixel), [Geist source and license](https://github.com/vercel/geist-font), [IBM Plex source and license](https://github.com/IBM/plex).

No font is universally accessible. WCAG does not prescribe a particular font family or a general minimum font size. Pixel text is not automatically prohibited. Choosing a monospaced or proportional font does not establish accessibility on its own. [GSA typography guidance](https://www.section508.gov/develop/fonts-typography/).

## What the standards require

| Criterion | Requirement relevant to this system |
| --- | --- |
| [1.4.3 Contrast, AA](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) | Normal text needs 4.5:1 contrast; qualifying large text needs 3:1. Large generally means 18 pt / 24 CSS px regular or 14 pt / about 18.67 CSS px bold. Thin or unusual glyphs can still be hard to read. We keep a 4.5:1 minimum for all planned text pairs, including pixel headings. |
| [1.4.4 Resize text, AA](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html) | Text, apart from the stated exceptions, must support enlargement to 200% without losing content or function. Browser zoom must remain available. |
| [1.4.10 Reflow, AA](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) | Vertical content must work at 320 CSS px without requiring scrolling in both directions, except content whose meaning requires a two-dimensional layout. This corresponds to a 1280 px viewport at 400% zoom. |
| [1.4.12 Text spacing, AA](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html) | Content must survive user overrides of line height to 1.5 times font size, paragraph spacing to 2 times, letter spacing to 0.12 times and word spacing to 0.16 times. These are override test values, not mandatory default styling. |
| [1.4.5 Images of text, AA](https://www.w3.org/WAI/WCAG22/Understanding/images-of-text.html) | Use actual text when the technology can deliver the presentation; the criterion includes customization and essential-presentation exceptions. Pixel font rendering is still real text. Do not replace UI labels with screenshots, outlines or decorative Unicode characters. |

Screen readers need meaningful HTML text, structure and accessible control names. They do not need a separate visual font. Keep headings as headings, preserve their text and avoid duplicating decorative copies in the accessibility tree.

## Our rules, not WCAG mandates

| Use | Typeface | Starting point |
| --- | --- | --- |
| Short screen titles | Geist Pixel Square | 32 / 40 px, 400 |
| Short section headings, brand marks | Geist Pixel Square | 24 / 32 px or larger, 400 |
| Hero and marketing headlines | Geist Pixel Square | 56 / 64 or 72 / 80 px, responsive |
| Navigation, buttons, form controls | IBM Plex Mono | 16 / 24 px, 500–600 |
| Body, agent responses, instructions | IBM Plex Mono | 16 / 26 px, 400 |
| Supporting labels and dense table text | IBM Plex Mono | 14 / 20 px, 400–600 |
| Errors, confirmations, important values | IBM Plex Mono | 16 / 24 px; never rely on color alone |
| Code and identifiers | IBM Plex Mono | 13 / 20 px, with zoom available |
| Slide headline / body | Pixel / Plex | 56 pt / 26 pt |
| 1080p title / support / captions | Pixel / Plex / Plex | 112 px / 44 px / 36 px |

Plex Mono uses 16 / 26 px for body text and normal tracking. Its wider character measure needs generous text columns and wrapping controls; check actual copy instead of shrinking the type to fit.

Keep pixel headlines brief, ideally one or two lines. Use normal tracking and the font's genuine 400 weight. Do not synthesize bold, force all-caps paragraphs, disable antialiasing, add glow or render text into bitmap images to intensify the effect. Pixel styling should come from the glyph design.

The 24 px threshold is a conservative starting point for this font and design. It is not an assurance that every user can read it or that any pixel font works at that size. Check actual wording, display quality, zoom and context. Essential actions remain in IBM Plex Mono even when their labels are short.

The **Plain typography** preference changes pixel headings to IBM Plex Mono and preserves content, order and layout. It is an additional product choice, not a WCAG requirement or a substitute for an accessible default. Avoid fixed-height text containers; allow wrapping and user styles. Preserve the original browser font rendering.

## Verification and limits

Validate the actual local font files, contrast pairs, narrow layouts, text enlargement, spacing overrides, keyboard access to the preference and fallback behavior. Record measured checks in `browser-validation.json`. A synthetic text-size or viewport check must not be described as a complete assistive-technology audit.

Before public release, test representative tasks with people who use magnification and with people who find stylized type difficult to read. Inspect screen-reader output and actual browser zoom on supported platforms. Review slides and compressed video at their real viewing size; use IBM Plex Mono for captions and small instructional overlays. Automated checks cannot prove universal legibility or full WCAG conformance.

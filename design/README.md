# Visual system for the application and communications

Draft **0.5 — October 9, 2026** unifies the application, presentation and launch video. David chose light beige, white work surfaces and a brighter orange accent, followed by Nucleo pixel icons from the free selection. The supplied Flow screenshot informs the relationship between surfaces and colors; its branding and private content are not included.

**English is the only product language.** This includes interface copy, accessible names, placeholders, loading and empty states, errors, sample tasks, agent-generated messages and descriptions, this guide, slides and video. Use `lang="en"` and English formatting. Preserve user-supplied data and historical evidence in their original form unless translation is requested. Internal project discussion may remain in Czech.

“Workspace” and “Learning workspace” are placeholders. The product name, logo and final marketing copy remain open. The visual character combines pixel headlines, quiet surfaces, generous spacing and pixel details and clear reading text.

## Files

| File | Purpose |
| --- | --- |
| [brand-guide.html](brand-guide.html) | Interactive guide, type specimen, palette, light/dark UI concepts, icons and motion |
| [tokens.json](tokens.json) | Shared values in a simple custom schema; not a declared DTCG format |
| [tokens.css](tokens.css) | Generated variables, local fonts, type roles and basic controls |
| [build_tokens.py](build_tokens.py) | JSON-to-CSS generator with no additional dependencies |
| [title-card.html](title-card.html) | 16:9 title template; 1920 × 1080 at a 1920 px viewport |
| [fonts](fonts) | Fonts, desktop weights, licenses and provenance |
| [icons/nucleo-pixel](icons/nucleo-pixel) | 20 Pixel Essential 1.0.1 SVGs, sprite, provenance and copyright notice |
| [accessibility-typography.md](accessibility-typography.md) | Sourced font decision, WCAG criteria and implementation boundaries |
| [validation.json](validation.json) | Calculated contrast and font glyph checks |
| [browser-validation.json](browser-validation.json) | Preview layout and interaction checks |

Open the guide directly in a browser. All assets are local, so it works offline. A local HTTP server enables clipboard copying where supported; otherwise the preview displays the HEX value.

## Palette

| Role | HEX | Use |
| --- | --- | --- |
| Beige | `#F5F2EC` | Application shell, navigation, explanatory slides |
| White | `#FFFFFF` | Main workspace, inputs, panels |
| Orange | `#FF8A3D` | Primary action, important moments, video title background |
| Orange hover | `#FF9C5C` | Primary action hover |
| Ink | `#292622` | Text and content on orange buttons |
| Sand | `#EBE5DA` | Selected rows and secondary surfaces |
| Muted text | `#756B60` | Labels on white or base beige |
| Decorative border | `#DED7CB` | Nonessential surface separation |
| Control border | `#8A7561` | Inputs and controls requiring a visible boundary |
| Dark orange | `#A94312` | Small links and focus on light backgrounds |

Use roughly 75% light neutral surfaces, 15% dark elements and 10% orange as a compositional guide. Orange may fill a title frame.

Ink on orange has **6.42:1** contrast, ink on beige **13.48:1**, and dark orange on beige **5.37:1**. White on orange is only **2.35:1**: use ink for text and essential icons on orange. Bright orange is unsuitable for small text or the sole control boundary on white or beige. These calculations follow [WCAG text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html); they are not a full application accessibility audit.

Orange identifies brand and primary actions. Green means success, amber review, red failure and blue testing. Include a word and symbol with every status. Exact foreground/background pairs are in `themes` in the JSON. Recheck contrast on new backgrounds, photography, transparency and video.

The application defaults to light. Dark tokens use warm dark surfaces and lighter text. A dark concept preview does not imply an implemented application setting.

## Typography

**Geist Pixel Square 400** is the brand voice: short screen and section headings, major slide headlines and launch titles. **IBM Plex Mono 400–700** handles reading, controls and technical details. David selected its fixed-width rhythm to reinforce the technical character of the pixel headings. This pairing is shared across the application, presentation and video.

| Role | Typeface | Size / line height | Weight |
| --- | --- | --- | --- |
| Display | Pixel Square | 72 / 80 px | 400 |
| Hero | Pixel Square | 56 / 64 px | 400 |
| Screen title | Pixel Square | 32 / 40 px | 400 |
| Short section heading | Pixel Square | 24 / 32 px | 400 |
| Lead | Plex Mono | 20 / 30 px | 400 |
| Body / agent responses | Plex Mono | 16 / 26 px | 400 |
| Controls | Plex Mono | 16 / 24 px | 500–600 |
| Supporting labels | Plex Mono | 14 / 20 px | 500 |
| Code / technical details | Plex Mono | 13 / 20 px | 400 |

Pixel starts at 24 px, uses normal tracking and real weight 400, and stays brief. Keep buttons, navigation, forms, tables, errors, instructions, long text and captions in IBM Plex Mono. Use sentence case. Keep paragraphs around 55–75 characters per line and numeric columns aligned with tabular figures. Do not synthesize bold or italics or disable antialiasing.

These are project design decisions. **WCAG does not mandate a particular font or universally prohibit pixel fonts.** It requires sufficient contrast, text enlargement, reflow and support for spacing overrides. Read the [sourced accessibility guidance](accessibility-typography.md) for exact criteria and their limits. The guide includes a **Plain typography** switch; `data-ds-type="plain"` changes display text to IBM Plex Mono. This option supplements a readable default.

CSS type roles use `rem`. Keep pixel titles at least 24 px at the default scale, allow browser zoom, and let long content wrap. No font choice alone guarantees accessibility for every reader.

## Interface and graphic motif

Use a white workspace inside a beige shell. Radii: 24 px for the main workspace, 16 px for panels, 10 px for controls and 6 px for small tags. Use a 4/8 px spacing rhythm, 16/24 px padding and 32/48 px section gaps.

Primary actions are orange with ink text; secondary actions are white with a visible border. Keep one dominant action per context. Interactive targets are at least 44 × 44 px. Focus uses a 3 px outline with a 3 px offset. Controls must remain readable without shadows.

Three connected square modules suggest accumulated experience. This decorative motif is not the final logo. Keep it subordinate to content in the workspace; it can dominate a title frame. Pixel details coexist with soft panel corners and readable IBM Plex Mono text.

Copy describes observed state and the next action: “Test failed”, “Needs review”, “Reuse”. “Verified” must reflect real tests in the running product. The guide labels its illustrative UI as a concept.

## Pixel icons

Use **Nucleo Pixel Essential**, preserving the **24 × 24 px grid, 2 px strokes and square caps**. Use 24 px in UI and 48 or 72 px for larger compositions. Avoid 20 px scaling, rounded caps, filters, arbitrary rotation or mixing in a smooth outline set.

The official [free selection](https://nucleoapp.com/free-pixel-icons) is distributed as [Pixel Essential](https://nucleoapp.com/react-packages?family=pixel). This project includes 20 icons from version 1.0.1. The archive was verified against its published SHA512. Shapes were extracted statically from React wrappers into SVG without changing their geometry or running package code; no npm package, skill or MCP was installed.

| Role | Local SVG |
| --- | --- |
| Projects | `folder-open.svg` |
| Learned skills | `book-magic-skill.svg` |
| Project rules | `sliders.svg` |
| Search | `magnifier.svg` |
| New task and submit | `plus.svg`, `paper-plane.svg` |
| Success, error, review, progress | `check.svg`, `xmark.svg`, `triangle-warning.svg`, `loader.svg` |
| Skills and composition | `layers.svg`, `nodes.svg` |
| Permissions and test results | `shield-check.svg`, `clipboard-check.svg` |
| History and reuse | `clock.svg`, `reuse.svg` |
| Other controls | `gear.svg`, `file.svg`, `user.svg`, `trash.svg` |

SVGs use `currentColor`: ink on light surfaces and orange buttons. Set decorative icons next to text to `aria-hidden="true"`; icon-only controls need an English accessible name. A 24 px icon still requires a 44 × 44 px click target. Pair loaders with a status label; rotation is optional.

Inline an SVG or embed `sprite.svg` definitions once, then use `<svg class="ds-icon" aria-hidden="true"><use href="#nucleo-folder-open"></use></svg>`. External `<img>` elements do not inherit `currentColor`. Framework components can be built from the included shapes.

Icons remain © Nucleo. The [Nucleo license](https://nucleoapp.com/license) permits up to 100 bundled icons in an open-source project with a copyright notice; this selection has 20. Preserve [NOTICE.txt](icons/nucleo-pixel/NOTICE.txt) and [sources.json](icons/nucleo-pixel/sources.json). Do not redistribute these as a standalone icon library. This free subset is not the entire paid Pixel family. Check the free selection before adding symbols; record separate provenance for any original artwork.

## Presentation

Use 16:9, with a reference canvas of 13.333 × 7.5 inches. Headlines: Geist Pixel Square 400 / 56 pt. Body: IBM Plex Mono 400–500 / 26 pt. Labels: IBM Plex Mono 500 / 16 pt. Keep at least 5% margins on all sides.

One main idea per slide, at most two text levels. Use beige for explanations, white panels for real product screens and orange for an opening slide. Enlarge relevant UI areas instead of showing an unreadable full-screen capture. All presentation text is English.

## Launch video

Start at 1920 × 1080, with safe margins of at least 96 px horizontally and 54 px vertically. Headlines: Geist Pixel Square 400 / 112 px. Supporting text: IBM Plex Mono 500 / 44 px. Labels: IBM Plex Mono 500 / 24 px. Captions: IBM Plex Mono 600 / 36 px, around 44 px line height, at most two lines, white on an opaque ink band.

For vertical video, rebuild the composition on a 1080 × 1920 canvas rather than cropping the center. Adjust safe areas for the actual destination player.

Motion: 120 ms feedback, 200 ms transitions, 400 ms expressive motion, modules staggered by 80 ms. The motif moves from lower left to upper right. Limit UI text movement to 8–16 px, avoid flashing and endless pulsing, and respect `prefers-reduced-motion`. Every static frame should make sense on its own.

The title template is not a finished launch video; its slogan is a draft. Show the running product and label concepts, simulations and limitations. See the [project brief](../docs/hackathon-brief.md) for competition delivery rules. Before export, verify font embedding, English copy and readability at reduced size.

## Fonts and licenses

Geist Pixel Square comes from the official [Vercel Geist repository](https://github.com/vercel/geist-font), pinned to revision `10dc7658f13c38a474cde201bb09a4617267545b`. IBM Plex Mono comes from the [Google Fonts distribution](https://github.com/google/fonts/tree/main/ofl/ibmplexmono) of [IBM Plex](https://github.com/IBM/plex). Files were verified against Git blob hashes; exact URLs and SHA256 hashes are in [sources.json](fonts/sources.json). Preserve both SIL OFL 1.1 notices: [Geist](fonts/geist-OFL.txt) and [IBM Plex](fonts/ibmplexmono-OFL.txt). No payment or operating-system installation was needed.

The web uses Pixel Square WOFF2 and original IBM Plex Mono TTFs. Original TTF files also support desktop editors: Pixel Square 400 and Plex Mono Regular 400, Medium 500, SemiBold 600 and Bold 700. No font binaries were modified. The font files remain local, so the guide also works offline.

## Implementation and validation

Copy the `design` directory or preserve font paths relative to the CSS. Add `ds-root` and `data-ds-theme="light"` to the application root, then use `ds-type-*`, `ds-button` and semantic `--ds-*` variables. The stylesheet does not apply a global reset or automatically restyle an existing UI.

Edit `tokens.json`, then run `python3 design/build_tokens.py`. The prototype imports `/design/tokens.css`; `web/style.css` assigns display and reading roles, and `web/typography.js` stores the optional plain-type preference. The generator also syncs a standalone `web/design-tokens.css` and web font assets for portable integration. Do not edit generated CSS manually. Preserve semantic roles when porting to another stack, and update slides and video rules together. Figma import requires mapping this custom JSON schema.

Version palette, font and scale changes, and update all examples. Run `python3 design/validate_design.py` to check contrast, font glyph coverage and local references; glyph checks use FontTools. `check_preview.cjs` uses Playwright and Chromium/Chrome; `DESIGN_CHROME_PATH` may point to an existing executable. Browser preview results cover layout, interactions, text enlargement and spacing overrides. `check_product_typography.cjs` checks the browser design preview with API interception and no model requests; it writes `browser-product-typography.json`. These checks do not establish full product accessibility or the correctness of agent tasks.

Current prototype layout limits (October 9): screenshot review found that the persistent sidebar clips main content at 320 CSS px, and its header clips controls under 200% text enlargement. These are open application layout issues; passing document-width checks do not resolve them. The standalone brand guide passes its separate layout and spacing checks.

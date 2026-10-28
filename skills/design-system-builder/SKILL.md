---
name: design-system-builder
description: >
  Builds a new design system from scratch from one of four inputs: a product brief, inspiration screenshots, a brand color palette, or a mix. Produces design tokens (color scales, typography, spacing, shape, elevation, motion), light and dark themes, component specs, and a contrast-verified output. Use when the user asks to "create a design system", "create a color palette", "define a spacing/typography scale", "set up theming/dark mode", "design tokens" or "style guide" for a new product. Not for changing the tokens of an existing codebase, and not for single-component or one-off page work (e.g. "build a landing page", "style this button").
license: MIT
model: sonnet
---

# Design System Builder

Builds a new design system from the input the user gives. Every run follows the same path: **identify the input mode → confirm a direction → build tokens → spec components → verify → deliver.**

## 1. Identify the input mode

| Mode | The user gives you | Direction comes from |
|---|---|---|
| **Autonomous** | A brief or nothing visual: "playful fintech app", a product type, an audience | You decide, from product type, audience and platform |
| **Screenshots** | Images of sites, apps or mockups they like | What you extract from the images |
| **Palette** | Hex/RGB/HSL values, a palette image, a logo, or brand colors | The palette is fixed; you design everything else around it |
| **Mixed** | Screenshots plus a palette | Palette wins for color. Screenshots drive type, spacing, shape, elevation and tone |

Edge inputs:

- **Text-only brief** (no colors, no images) → Autonomous.
- **Logo image** → treat as Palette: pull the dominant brand colors from it.
- **URL or Figma link** you cannot open or view → say so, and ask for screenshots or exported colors. Never invent what the page looks like.
- **A single brand color or a font name only** → Palette mode with a sparse input (see §3).
- **Screenshots of a named competitor or product with "make it like this"** → extract tone and structure, but build original tokens. Do not reproduce their exact palette or branding.

## 2. Minimum inputs, then ask once

You need these before building. Take whatever the user already stated and ask for the rest **in a single batch**, never one question at a time:

- Product type and audience (needed for Autonomous; helpful for all modes)
- Platform: web (Tailwind v4 or plain CSS), native iOS/Android, or both. This decides the output format (§6).
- Accessibility target. **Default to WCAG 2.2 AA** if unstated.
- Light only, dark only, or both. **Default to both.**
- Anything fixed that you must keep: brand colors, fonts, an existing logo.

If the user says "just do it" or the session cannot be interactive, apply the defaults and list them as assumptions in the direction summary.

## 3. Establish and confirm the direction

Produce a **Direction Summary** before writing any tokens. It starts with a **theme name**: a short, one-word name that fits the direction (e.g. `Ember`), or the name the user gave. The name becomes the output folder (§6). It then states, with concrete values: the color roles and brand hues (hex), neutral temperature, typeface choices, type scale ratio, spacing base and density, corner radius, elevation style, motion feel, and overall tone. Say why for each choice. Then **wait for the user to confirm or redirect.** The checkpoint applies to every mode. Skip the wait only if the user has said to proceed without confirming; in that case state the summary and continue.

Mode-specific rules:

**Autonomous.** Pick a direction that fits the product and audience, and justify it in a sentence each. Avoid defaulting to a generic blue-and-gray palette without a reason.

**Screenshots.**
- Extract palette, type style, spacing density, corner radius, elevation and tone. Do not copy layout or branding.
- Colors read from images are **approximations**. Say so, and round to clean values.
- If screenshots disagree (e.g. one light, one dark, or two unrelated palettes), report the conflict in the summary and propose which signal wins, rather than averaging them.
- JPEG artifacts, gradients and photos distort sampling. Use flat UI regions and note low confidence where relevant.

**Palette.**
- Brand colors are fixed inputs. Build tonal scales and semantic roles around them.
- Check every text/background pairing at the target contrast level (default AA). **Never silently change a brand color.** When a pair fails: report it, propose the nearest passing alternative (a darker or lighter step, or a different pairing), and keep the original brand value available for logos and decorative use.
- **Brand fails AA as a fill.** When the brand color cannot carry a label at the target contrast on the light surface, move the **light-mode** fill to the nearest step of the same hue that passes, and keep the original brand value as its own pinned primitive. Use the original as the dark-mode fill if it passes there. The `on-*` label then flips with the theme, so state in the docs that a fill is always paired with its `on-*` token. Text in the brand hue gets its own `--color-text-brand` token a step darker than the fill in light mode so it also passes on tinted backgrounds.
- **Sparse palettes.** With only one brand color, derive the neutrals, the secondary/accent (if needed) and the success/warning/error roles yourself, and mark them as derived in the summary. If the palette has no neutrals or feedback colors, derive those the same way.
- Match the palette's temperature when deriving neutrals: tint them slightly toward the brand hue.

**Mixed.** Palette defines brand colors. Screenshots define type, spacing, shape, elevation and tone. Neutrals and feedback colors come from the palette if present; otherwise derive them to suit the screenshots' tone.

## 4. Build

### Token architecture (three layers)

1. **Primitive**: raw values. `--primitive-{category}-{name}`. Never used by components directly.
2. **Semantic**: purpose-based, pointing at primitives. `--color-text-primary`, `--space-section-gap`, `--radius-control`. This is the layer product code uses.
3. **Component**: per-component decisions pointing at semantic tokens. `--button-primary-bg`, `--input-border-focus`.

See [references/tokens.example.css](references/tokens.example.css) for a complete, checker-verified example of all three layers, both themes, and the accessibility media queries. It shows structure and completeness, **not a palette to reuse.**

### Token rules

- **No raw values in the semantic or component layers.** Everything points at a token one layer down (e.g. no literal `white`).
- **Every fill that carries text gets an `on-*` partner** (`--color-primary` / `--color-on-primary`, the same for success, warning, error, info). No hardcoded `white` or `black` for text on color.
- **Define every primitive you reference.** Each hue used gets a full 50–950 scale (the example abbreviates green/amber/red for brevity; real output should not).
- **Complete categories.** Color, spacing, typography (family, size, weight, line-height, letter-spacing), radius, shadow/elevation, z-index, motion (duration, easing), focus ring. Document breakpoints too, in comments or the docs, since `var()` cannot be used inside `@media`.
- **Scales must be derivable.** Type: a modular ratio (state it). Spacing: a base unit (state it) with deliberate gaps. Color: even lightness steps tuned per hue, not one chroma value for all steps.
- **Color in OKLCH, in sRGB gamut.** The checker warns on out-of-gamut values. Lower the chroma, or state explicitly that you are targeting Display-P3. Provide hex fallbacks (`check_contrast.py --hex` prints them) when supporting browsers without `oklch()`.
- **Sizes in `rem`** so user font-size settings and zoom work.
- **Color roles.** For `primary`, any secondary, and each feedback status (`success`, `warning`, `error`, `info`): `--color-{role}` is the solid fill, `--color-on-{role}` its label, `--color-{role}-subtle` a tinted background, and `--color-{role}-text` the AA-safe text/icon color on surfaces (for the brand, `--color-text-brand`).
- **Start `tokens.css` with a header comment** covering: the name and version, the three layers, how themes switch, breakpoints (documented there because `var()` cannot be used in `@media`), expected fonts and how to load them, and any brand-contrast decision (which step is the fill in each theme and why).
- **Density modes (optional).** If the product has dense data UIs (tables, grids, dashboards), add `[data-density="compact" | "comfortable"]` scopes that re-declare row, header and cell-padding tokens. The unmarked setting is the middle one. Touch devices (`pointer: coarse`) still get 44px targets.
- **Consistent naming**: kebab-case, same word order everywhere. Figma maps by replacing `-` with `/` at role boundaries (`--color-text-primary` ↔ `color/text/primary`).

### Theming and dark mode

- Build light and dark unless told otherwise. A dark theme **overrides every color token whose value should change**, not a handful. This includes surfaces, borders, brand, feedback, shadows and on-colors.
- Dark themes use lighter, less saturated brand and feedback colors. **Hover and active states get lighter on dark surfaces**, not darker.
- Support both an explicit toggle (`[data-theme="dark"]`) and the OS preference (`@media (prefers-color-scheme: dark)`). The toggle wins: `:root:not([data-theme="light"])` inside the media query. Set `color-scheme` on each theme.

### Components

Pick the inventory from the product. A typical set: Button, Input, Select, Checkbox/Radio/Switch, Card, Badge, Alert/Toast, Modal, Tabs, Tooltip. **Fully specify at least Button, Input, Card and Alert**, and list the rest with their variants and states.

`components.md` is laid out as:

1. **Intro**: which components are fully specified and which are summarized, and that all of them read component tokens from `tokens.css`.
2. **Rules that apply to every interactive component**: a table (rule → how it is met) built from the accessibility requirements below, plus any system-specific rule (for example, a brand fill and its label flipping together between themes).
3. **One section per fully specified component**, in this order: **Variants** table (use, fill, label, edge), **Sizes** table (height token, visual size, padding, font), **States** table (default, hover, active, focus-visible, disabled, loading, error where applicable, with contrast ratios where they matter), **Composition** rules, **markup** for the chosen stack (Tailwind classes or plain CSS), and a **Do / Don't** pair. Separate sections with `---`.
4. **Product-specific component** (optional, one full section): if the product's core UI is something dense like a data grid, specify it with a parts → tokens table and density table.
5. **Remaining components**: one table with columns Component, Variants, States, Tokens, Notes.
6. **Patterns** (optional): how the same tokens apply to marketing or content pages (display type, section spacing, content width).

Accessibility requirements that apply to every interactive component:
- Visible focus indicator (`:focus-visible`) with ≥3:1 contrast against its surroundings, via a focus-ring token.
- Pointer targets ≥44px (WCAG 2.5.8 requires 24px minimum, platforms recommend 44px). If the visual size is smaller, grow the hit area or switch to 44px on `(pointer: coarse)`. Specs must not contradict this (e.g. a 32px button with a "44px target" line and no mechanism).
- Disabled and loading states use `aria-disabled` / `aria-busy` where the element must stay focusable.
- Feedback states (success/warning/error) never rely on color alone: include an icon or text.
- Respect `prefers-reduced-motion` (collapse durations) and `forced-colors` (fall back to system colors for focus and borders).

## 5. Verify before delivering

1. Run the contrast policy script on the design system folder. Run it from the skill folder, or adjust the paths:
   ```
   ./scripts/check-contrast.sh <theme-name>
   ```
   It runs `scripts/check_contrast.py`, which resolves `var()` chains, checks both themes, and warns about out-of-gamut colors. The script holds the list of pairs that must pass (text on every surface it can sit on, brand and status text on their tints, on-color/fill, input error border, focus ring on every surface; text 4.5:1, non-text UI 3:1). Pairs whose tokens you did not define are skipped. It prints the result and writes it to `contrast-reports/<theme-name-lowercase>.txt` beside the design system folder. To check extra tokens, call `python3 -I scripts/check_contrast.py <theme-name> --pair FG BG MIN`. A known, documented exception can be passed with `--allow FG BG`; it is reported as KNOWN, not a failure.
2. Fix every FAIL by adjusting the **derived** tokens or step choice. For Palette-mode brand colors, follow the failure rule in §3 instead of editing the brand value.
3. Confirm no `var()` references an undefined token (the checker errors on these) and that both themes pass.
4. Generate `tokens.json` with `python3 -I scripts/build_tokens_json.py <theme-name>` after the last edit to `tokens.css`.
5. Check that `preview.html` hard-codes no color, size or font value of its own: everything comes from `tokens.css`.
6. The report file is the checker's output. If you could not run the scripts, say so plainly instead of claiming the pairs pass.

## 6. Deliverables and output format

Write the design system to `<theme-name>/` (e.g. `Ember/`) in the working directory, unless the user names a location. Use the theme name from the Direction Summary, capitalized, with no spaces. Every design system folder has the same shape:

| File | Contents |
|---|---|
| `tokens.css` | **Source of truth.** All three layers, light and dark themes, density modes if used, accessibility media queries, header comment (§4) |
| `tokens.json` | W3C DTCG export for Figma (Tokens Studio) and Style Dictionary. Generated by `scripts/build_tokens_json.py`. Never edited by hand |
| `tailwind-theme.css` | Tailwind v4 preset (web with Tailwind only). See below |
| `components.md` | Component specs, laid out as in §4 |
| `README.md` | See below |
| `preview.html` | Visual reference page: palette, type scale, controls, feedback, the product-specific component, light and dark. Links `tokens.css` and takes every value from it. Has a theme toggle and a density switch if density modes exist. Self-contained apart from fonts |

The contrast report is written outside the folder, to `contrast-reports/<theme-name-lowercase>.txt` next to it, one file per design system.

**`tailwind-theme.css`.** Imports `./tokens.css`, then exposes it in a `@theme inline` block so each utility points at a CSS variable and light/dark switching needs no `dark:` prefixes. It also defines a `dark` custom variant that follows both `[data-theme]` and the OS preference. Rules:
- Utility names deliberately differ from the CSS variable names (`bg-canvas`, not `bg-surface`), so a theme entry never shadows the variable it reads.
- It removes Tailwind's default palette (`--color-*: initial`) so only system colors exist; comment that deleting that line restores the defaults.
- Open with a header comment that is a compact cheat sheet: usage, then one line per utility group (surface, text, border, brand, secondary, status, shape/depth, focus, palette), then the fill/label pairing rule.

**`README.md`** sections, in order: title and one-paragraph summary, Contents (file table), Direction (table: area, choice, why), brand contrast notes with a do/don't table (when the brand color was adjusted), Using it (Tailwind, plain CSS, utility cheat sheet mapping token roles to utilities, distribution), Token architecture (layers diagram and rules), Naming guide (`--{category}-{role}[-{variant}][-{state}]` with examples per category, the color-role pattern, scales), Themes and density, Figma naming map (CSS variable ↔ Figma variable ↔ `tokens.json` path; light/dark are Figma modes, dark aliases live in `$extensions.mode.dark`), Working on the system (how to run the two scripts), Versioning, and What is derived vs given.

Format by platform:
- **Web with Tailwind (default)**: `tokens.css`, `tailwind-theme.css`, `tokens.json`.
- **Web without Tailwind**: `tokens.css` and `tokens.json`. Omit `tailwind-theme.css` and show plain-CSS usage in the README.
- **Native iOS/Android or multi-platform**: `tokens.json` is the main artifact, plus a short mapping to platform primitives (Color/Font assets, `MaterialTheme`) in the README. Use dp/pt, not rem. CSS-only pieces (media queries, `color-scheme`, `preview.html`, `tailwind-theme.css`) do not apply; keep `tokens.css` as the source `tokens.json` is generated from.

Versioning notes (kept to a few lines in the README), starting at `0.1.0`: semantic versioning for the token set. Major: renaming or removing a token, or changing its meaning. Minor: adding tokens, components or variants. Patch: value tweaks that keep every contrast pair passing. Deprecate by keeping the old token as an alias with a comment for one minor release, then remove it in the next major. Name the brand colors that never change in a minor or patch release.

## 7. Reply style

Chat replies stay short: the direction summary, the assumptions you made, the checker result, and the list of files written (the folder and the contrast report). The detail lives in the files. Explain the reasoning behind each major choice in a sentence, and flag anything derived or approximated.

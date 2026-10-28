# Design System Builder Skill

The design system builder skill creates a new design system from scratch. You give it a product brief, inspiration screenshots, a brand palette, or a mix. It returns design tokens, light and dark themes, component specs, and a contrast report that has been checked against WCAG.

The skill is for new products. It does not change the tokens of an existing codebase, and it does not build single components or one-off pages such as a landing page.

## What Is in This Folder

Paths are relative to the skill folder, `skills/design-system-builder/`, inside the ai-toolkit plugin.

| Path                           | Purpose                                                                           |
| ------------------------------ | --------------------------------------------------------------------------------- |
| `SKILL.md`                     | The skill itself. Defines the workflow, token rules, and deliverables.            |
| `README.md`                    | This file.                                                                        |
| `references/tokens.example.css` | A complete example of the three token layers, both themes, and accessibility queries. It shows structure only. It is not a palette to reuse. |
| `scripts/check_contrast.py`    | Contrast engine. Takes a design system folder, resolves `var()` chains and tests color pairs in both themes. |
| `scripts/check-contrast.sh`    | Contrast policy. Holds the pairs that must pass, runs the engine and writes `contrast-reports/<name>.txt`. |
| `scripts/build_tokens_json.py` | Generates `tokens.json` (W3C DTCG) from a folder's `tokens.css`. |

## How the Skill Works

1. The skill identifies your input mode (autonomous, screenshots, palette, or mixed).
2. It asks for any missing inputs in a single batch of questions.
3. It writes a direction summary with concrete values and waits for you to confirm or redirect.
4. It builds the tokens, the themes, and the component specs.
5. It runs the contrast checker, fixes failures, and writes the files.

## Input Modes

| Mode        | You provide                                                  | Where the direction comes from                                     |
| ----------- | ------------------------------------------------------------ | ------------------------------------------------------------------ |
| Autonomous  | A brief or product type, such as "playful fintech app"       | The skill decides from product type, audience, and platform        |
| Screenshots | Images of sites, apps, or mockups you like                   | What the skill extracts from the images                            |
| Palette     | Hex, RGB, or HSL values, a palette image, or a logo          | The palette is fixed. The skill designs everything else around it  |
| Mixed       | Screenshots and a palette                                    | Palette sets color. Screenshots set type, spacing, shape, and tone |

A few cases behave in a specific way:

- A text-only brief with no colors or images runs in autonomous mode.
- A logo image is treated as a palette. The skill pulls the dominant brand colors from it.
- A single brand color or a font name is a sparse palette. The skill derives the neutrals, accents, and feedback colors and marks them as derived.
- A URL or Figma link that the skill cannot open is not guessed at. It asks for screenshots or exported colors instead.
- A "make it like this" request for a named product extracts tone and structure only. The skill builds original tokens and does not copy the other brand's palette.

## Using the Skill

### Step 1: Start the Skill

In Claude Code, open the folder where you want the design system and describe what you want. Any of these phrases triggers the skill:

- `create a design system`
- `create a color palette`
- `define a spacing and typography scale`
- `set up theming and dark mode`
- `design tokens` or `style guide` for a new product

Include as much as you know. For example:

```text
create a design system for a playful fintech app for students, web only, light and dark
```

```text
create a design system from these screenshots and our brand colors #1F6FEB and #F5A524
```

### Step 2: Answer the Questions

The skill needs five inputs. It uses what you already stated and asks for the rest once.

| Input                | Default if you do not say        |
| -------------------- | -------------------------------- |
| Product type and audience | None for autonomous mode. Required. |
| Platform             | Web                              |
| Accessibility target | WCAG 2.2 AA                      |
| Themes               | Light and dark                   |
| Fixed constraints    | None. Brand colors, fonts, logo. |

If you say "just do it", the skill applies the defaults and lists them as assumptions.

### Step 3: Review the Direction Summary

Before it writes any tokens, the skill posts a direction summary. It covers:

- color roles and brand hues in hex
- neutral temperature
- typefaces and the type scale ratio
- spacing base and density
- corner radius, elevation style, and motion feel
- overall tone, with a reason for each choice

Confirm it or ask for changes. This checkpoint applies to every mode. To skip it, tell the skill to proceed without confirming.

In screenshots and mixed modes, colors read from images are approximations. The summary says so, and it reports any conflict between screenshots instead of averaging them.

### Step 4: Review the Output

The skill names the theme in its direction summary (for example `Ember`) and writes to a folder of that name, `<theme-name>/`, in the working directory unless you name another location.

| File                 | Contents                                                                                       |
| -------------------- | ---------------------------------------------------------------------------------------------- |
| `tokens.css`         | Source of truth. Primitive, semantic, and component tokens. Light and dark themes, density modes if used, accessibility media queries. |
| `tokens.json`        | W3C DTCG export for Figma (Tokens Studio) and Style Dictionary. Generated from `tokens.css`.   |
| `tailwind-theme.css` | Tailwind v4 preset that imports `tokens.css` and exposes it as utilities. Only for web with Tailwind. |
| `components.md`      | Component specs. Button, Input, Card, and Alert are fully specified. Others list variants and states. |
| `README.md`          | Direction rationale, brand contrast notes, usage, naming guide, Figma naming map, versioning notes. |
| `preview.html`       | Visual reference page for the palette, type, controls and feedback, in light and dark.         |

The contrast report is written next to the folder, to `contrast-reports/<theme-name-lowercase>.txt`.

Native iOS or Android projects get `tokens.json` plus a short mapping to platform primitives in the README. Sizes use dp or pt. The CSS-only files do not apply.

The chat reply stays short. It lists the direction summary, the assumptions, the checker result, and the files written.

### Step 5: Use the Tokens

Product code uses the semantic layer only, for example `--color-text-primary` or `--radius-control`. Component styles use the component layer, for example `--button-primary-bg`. Nothing outside `tokens.css` should reference a `--primitive-*` token.

To switch themes, set `data-theme` on the root element:

```html
<html data-theme="dark">
```

Without `data-theme`, the theme follows the operating system setting. An explicit `data-theme="light"` overrides a dark OS preference.

## Token Architecture

| Layer     | Naming                              | Purpose                                              |
| --------- | ----------------------------------- | ---------------------------------------------------- |
| Primitive | `--primitive-{category}-{name}`     | Raw values. Components never use them directly.      |
| Semantic  | `--color-text-primary`              | Purpose-based tokens that point at primitives.       |
| Component | `--button-primary-bg`               | Per-component decisions that point at semantic tokens. |

Other rules the skill follows:

- Every fill that carries text has an `on-*` partner, such as `--color-primary` and `--color-on-primary`.
- Colors use OKLCH inside the sRGB gamut, with hex fallbacks on request.
- Sizes use `rem` so browser font settings and zoom work.
- The dark theme overrides every color token whose value should change.
- Names are kebab-case. Figma maps them by replacing `-` with `/` at role boundaries.

## Running the Contrast Checker Yourself

The skill runs the checks for you. You can rerun them after editing the tokens. Run these from the skill folder, or adjust the paths:

```bash
./scripts/check-contrast.sh <theme-name>             # check and write contrast-reports/<theme-name>.txt
python3 -I scripts/build_tokens_json.py <theme-name>  # regenerate tokens.json after editing tokens.css
```

`check-contrast.sh` passes its list of pairs to `check_contrast.py`. Pairs whose tokens are not defined are skipped. The checker tests both themes. Text pairs need 4.5:1. Non-text UI such as borders and the focus ring needs 3:1. It exits with code 1 if any pair fails or any color cannot be parsed. It also warns about colors outside the sRGB gamut and errors on a `var()` that points to an undefined token.

Two options help with custom work:

```bash
# Add a pair for an extra token, such as a secondary accent
python3 -I scripts/check_contrast.py <theme-name> --pair --color-text-brand --color-surface 4.5

# Print resolved hex values per theme, for browsers without oklch()
python3 -I scripts/check_contrast.py <theme-name> --hex
```

## Brand Colors That Fail Contrast

In palette mode, the skill never changes a brand color on its own. When a pairing fails, it reports the failure and proposes the nearest passing alternative, such as a darker or lighter step or a different pairing. The original brand value stays available for logos and decorative use. If the brand color cannot carry a label as a fill on the light surface, the light-mode fill moves to the nearest passing step and the original becomes the dark-mode fill, with the label color flipping between themes.

## Installing the Skill

### From the plugin marketplace

In Claude Code, add the marketplace and install the plugin:

```text
/plugin marketplace add vipulchauhan24/ai-toolkit
/plugin install ai-toolkit@product-development
```

### Manually

Copy the `skills/design-system-builder/` folder into a skills directory that Claude Code reads:

- Project level: `.claude/skills/design-system-builder/`
- User level: `~/.claude/skills/design-system-builder/`

Keep `references/` and `scripts/` inside the skill folder. `SKILL.md` links to both by relative path.

## Customizing the Skill

All paths below are relative to the skill folder.

- Edit the defaults in section 2 of `SKILL.md` to change the accessibility target or the default themes.
- Edit the token rules in section 4 to change naming, units, or the color space.
- Edit the deliverables table in section 6 to change file names or the output location.
- Replace `references/tokens.example.css` if you want the skill to follow a different structure.

# System

The base every project shares. It makes separate projects consistent: the same scale of space and type, the same control sizes, the same way of building a page. Projects differ only in what `DESIGN.md` sets.

Read this file for every build. Then read only the files you need.

| You are deciding | Read |
|---|---|
| Margins, padding, gaps, widths | `spacing.md` |
| Font sizes, line height, font loading | `typography.md` |
| Colour, themes, contrast | `color.md` |
| Page structure, alignment, empty space | `layout.md` |
| Behaviour at each screen size | `responsive.md` |
| Radius, borders, shadows, layering | `elevation.md` |
| The accessibility floor | `accessibility.md` |
| Loading, empty, error, disabled and other states | `states.md` |
| Dashboards, tables, settings, screens people work in | `app-screens.md` |
| How things move | `../motion/motion.md` |
| One component | `../components/<name>.md` |
| One section of a page | `../sections/<name>.md` |

## What is fixed and what varies

| Fixed in every project | Set per project in `DESIGN.md` |
|---|---|
| The spacing scale and page widths | Font pairing |
| The type roles and their sizes | Palette |
| Control heights and tap targets | Radius family: sharp, tight, soft or round |
| Centred layout with equal margins | Density: comfortable or compact |
| How each component is built | Which sections exist, their order and variants |
| Accessibility floor | Motion level and optional effect |
| | Type contrast, section backgrounds, heading alignment, image treatment |
| | The concept, and one section built from scratch |

Never change a fixed value for one project. If something does not fit, change the layout.

## The rules

1. Use tokens. Write no raw colour, and no spacing or font size outside these lists.
2. Custom CSS is allowed, and it reads these tokens.
3. Every page sits in a centred container with equal left and right margins (`layout.md`).
4. One accent colour, two font families at most, one button style pair, one card style per project.
5. Every interactive element has hover, focus, active and disabled states.
6. Icons come from Tabler Icons only (`../components/icon.md`).

## Tokens

This is the complete list. Component and section files may use only these names.

### Space

| Token | Value |
|---|---|
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 12px |
| `--space-4` | 16px |
| `--space-5` | 20px |
| `--space-6` | 24px |
| `--space-8` | 32px |
| `--space-10` | 40px |
| `--space-12` | 48px |
| `--space-16` | 64px |
| `--space-20` | 80px |
| `--space-24` | 96px |
| `--gutter` | `clamp(24px, 4.5vw, 64px)`: the page's side margin |
| `--section` | `clamp(64px, 8.5vw, 120px)`: padding above and below a section |
| `--grid-gap` | `clamp(16px, 2vw, 24px)`: gap between grid columns |
| `--container` | 1200px |
| `--container-wide` | 1440px |
| `--container-narrow` | 880px |
| `--prose` | 68ch |
| `--nav-height` | 64px |

### Type

| Token | Value |
|---|---|
| `--font-display` | Headings, from `DESIGN.md` |
| `--font-body` | Text and interface, from `DESIGN.md` |
| `--font-mono` | Code and IDs |
| `--text-xs` | 12px |
| `--text-sm` | 14px |
| `--text-base` | 16px |
| `--text-lead` | `clamp(1.125rem, 1.05rem + 0.3vw, 1.25rem)`: 18 to 20px |
| `--text-h3` | `clamp(1.25rem, 1.1rem + 0.4vw, 1.5rem)`: 20 to 24px |
| `--text-h2` | `clamp(1.75rem, 1.379rem + 1.524vw, 2.75rem)`: 28 to 44px |
| `--text-h1` | `clamp(2.25rem, 1.6rem + 2.667vw, 4rem)`: 36 to 64px |
| `--text-display` | `clamp(2.75rem, 1.543rem + 4.952vw, 6rem)`: 44 to 96px |
| `--leading-tight` | 1.05 |
| `--leading-snug` | 1.25 |
| `--leading-normal` | 1.6 |
| `--tracking-display` | -0.03em |
| `--tracking-tight` | -0.02em |

### Controls

| Token | Value |
|---|---|
| `--control-sm` | 32px |
| `--control-md` | 40px |
| `--control-lg` | 48px |
| `--touch` | 44px: smallest tap target on touch screens |

### Shape and depth

| Token | Value |
|---|---|
| `--radius-sm` | From the radius family |
| `--radius-md` | From the radius family |
| `--radius-lg` | From the radius family |
| `--radius-full` | 9999px |
| `--shadow-1` | Resting raised surface, faint |
| `--shadow-2` | Dropdowns and popovers |
| `--shadow-3` | Modals |
| `--z-nav` | 100 |
| `--z-dropdown` | 200 |
| `--z-modal` | 300 |
| `--z-toast` | 400 |
| `--z-tooltip` | 500 |

### Motion

| Token | Value |
|---|---|
| `--duration-press` | 100ms |
| `--duration-hover` | 150ms |
| `--duration-enter` | 250ms |
| `--duration-exit` | 180ms |
| `--duration-reveal` | 400ms |
| `--ease-out` | `cubic-bezier(0.22, 0.8, 0.3, 1)` |
| `--ease-in` | `cubic-bezier(0.5, 0, 0.9, 0.4)` |
| `--ease-in-out` | `cubic-bezier(0.45, 0, 0.2, 1)` |

### Colour

All values come from the palette and switch with the theme.

| Token | Used for |
|---|---|
| `--bg` | Page background |
| `--surface` | Cards, panels |
| `--surface-2` | Hover fills, wells, inset areas |
| `--ink` | Main text |
| `--ink-2` | Secondary text |
| `--ink-3` | Hints and metadata, still 4.5:1 |
| `--line` | Dividers, card edges |
| `--line-strong` | Control borders, 3:1 |
| `--accent` | Main action and key emphasis |
| `--on-accent` | Text on the accent |
| `--accent-soft` | Tinted background for the accent |
| `--positive` `--positive-soft` | Success |
| `--negative` `--negative-soft` | Errors, destructive actions |
| `--warning` `--warning-soft` | Caution |
| `--focus` | Focus ring |
| `--link` `--link-line` | Text links and their underline. Links take the action colour only when it reads as text at 4.5:1 |
| `--accent-2` `--on-accent-2` | A second button colour, only for two distinct actions of similar weight |
| `--band` `--band-ink` `--band-ink-2` `--band-ink-3` `--band-line` | Banded section backgrounds and the text and lines on them |
| `--highlight` `--on-highlight` | Tags, badges and markers |

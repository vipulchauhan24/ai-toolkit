# Design

Written by `deal.py`. Later work reads this file and does not re-decide the look. To change it, edit this file and `design.css` together.

- Kind: portfolio
- Kit version: 0.1.0
- Material available: experience, numbers, quotes
- Concept: none: dealt at random

## Theme and atmosphere

Palette `olive-bone-mustard` (Olive, bone and mustard), type `bricolage-dm` (characterful), radius family `soft`, density `comfortable`.

Add one or two sentences here on how this should feel, from the fact sheet and voice in `COPY.md`.

## Colour

Combo `olive-bone-mustard` (Olive, bone and mustard): olive `#2A2B1E`, bone `#F4F1E8`, mustard `#E3B23C`. Roles: text is olive, background is bone, highlight is mustard.

Every colour is set here before any code. Use the tokens; never write a colour value in a component.

| Token | Light | Dark | Used for |
|---|---|---|---|
| `--bg` | `#F4F1E8` | `oklch(18.0% 0.023 111.4)` | Page background |
| `--surface` | `oklch(98.3% 0.005 91.5)` | `oklch(22.5% 0.023 111.4)` | Cards and panels |
| `--surface-2` | `oklch(92.3% 0.012 91.5)` | `oklch(27.0% 0.023 111.4)` | Inputs, wells and hover fills |
| `--ink` | `#2A2B1E` | `oklch(95.8% 0.012 91.5)` | Headings and bold text |
| `--ink-2` | `oklch(48.6% 0.019 107.7)` | `oklch(72.5% 0.015 100.3)` | Body text |
| `--ink-3` | `oklch(53.3% 0.019 106.6)` | `oklch(61.6% 0.017 103.3)` | Dates, captions and labels |
| `--line` | `oklch(86.4% 0.014 96.1)` | `oklch(28.9% 0.021 109.8)` | Dividers |
| `--line-strong` | `oklch(62.8% 0.017 104.2)` | `oklch(52.2% 0.018 105.5)` | Control borders |
| `--accent` | `#2A2B1E` | `oklch(95.8% 0.012 91.5)` | Primary button and key emphasis |
| `--on-accent` | `#F4F1E8` | `oklch(18.0% 0.023 111.4)` | Primary button label |
| `--accent-soft` | `oklch(86.4% 0.014 96.1)` | `oklch(28.9% 0.021 109.8)` | Soft accent fills |
| `--link` | `#2A2B1E` | `oklch(95.8% 0.012 91.5)` | Text links |
| `--link-line` | `#2A2B1E` | `oklch(95.8% 0.012 91.5)` | Link underline |
| `--focus` | `#2A2B1E` | `oklch(95.8% 0.012 91.5)` | Focus ring |
| `--accent-2` | `#2A2B1E` | `oklch(95.8% 0.012 91.5)` | Second button, when the page has two distinct actions |
| `--on-accent-2` | `#F4F1E8` | `oklch(18.0% 0.023 111.4)` | Second button label |
| `--band` | `oklch(98.3% 0.005 91.5)` | `oklch(22.5% 0.023 111.4)` | Banded section backgrounds |
| `--band-ink` | `#2A2B1E` | `oklch(95.8% 0.012 91.5)` | Headings on a band |
| `--band-ink-2` | `oklch(48.6% 0.019 107.7)` | `oklch(72.5% 0.015 100.3)` | Body text on a band |
| `--band-ink-3` | `oklch(53.3% 0.019 106.6)` | `oklch(61.6% 0.017 103.3)` | Captions on a band |
| `--band-line` | `oklch(86.4% 0.014 96.1)` | `oklch(28.9% 0.021 109.8)` | Dividers on a band |
| `--highlight` | `#E3B23C` | `oklch(36.0% 0.072 85.2)` | Tags, badges and markers |
| `--on-highlight` | `#2A2B1E` | `oklch(95.8% 0.012 91.5)` | Text on a highlight |

- Text links: `--link`, underlined in `--link-line`. They use the action colour only when it reads as text.
- A second button is an outline (`.btn--secondary`).
- A band (`data-bands="banded"`) switches text to the `--band-ink` set for that section.

Status colours use the kit's defaults.

## Typography

- Display: Bricolage Grotesque
- Body: DM Sans
- Install: `npm install @fontsource-variable/bricolage-grotesque @fontsource-variable/dm-sans`

Sizes and weights come from `references/system/typography.md`.

## Shape

Radius family `soft` (6px / 8px / 12px). Density `comfortable`.

## Layout

Centred container with equal margins, as in `references/system/layout.md`.

Type contrast `quiet`, section backgrounds `plain`, headings `left`, images `none`.

Set these on `html`, and load `base/direction.css` after `base.css`:

`data-radius="soft" data-type="quiet" data-bands="plain" data-heads="left" data-images="none"`

## Sections

| Order | Section | Variant | Notes |
|---|---|---|---|
| 1 | `hero` | `name-led` |  |
| 2 | `experience` | `timeline` |  |
| 3 | `about` | `text-only` |  |
| 4 | `testimonials` | `two-column` |  |
| 5 | `proof-stats` | `row` |  |
| 6 | `contact` | `direct` |  |
| 7 | `footer` | `minimal` |  |

Drop any section the fact sheet can't support. Do not add a section with no real material.

## Motion

Level `standard`. Rules are in `references/motion/`.

## Do and don't

Do: use only kit tokens, one accent, Tabler icons, real content.

Don't: use placeholder sections, a second accent, or a layout that changes the fixed values in `references/system/system.md`.

## Responsive

Checked at 390, 768, 1024, 1440 and 1920, as `references/system/responsive.md` describes.

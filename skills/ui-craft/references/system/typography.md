# Typography

## Roles

| Role | Token | Weight | Line height | Tracking | Font |
|---|---|---|---|---|---|
| Display: the largest hero headline | `--text-display` | 500 to 600 | `--leading-tight` | `--tracking-display` | Display |
| Page title, h1 | `--text-h1` | 500 to 600 | `--leading-tight` | `--tracking-display` | Display |
| Section title, h2 | `--text-h2` | 500 to 600 | `--leading-snug` | `--tracking-tight` | Display |
| Subsection, h3 | `--text-h3` | 500 to 600 | `--leading-snug` | none | Display or body |
| Lead paragraph | `--text-lead` | 400 | `--leading-normal` | none | Body |
| Body | `--text-base` | 400 | `--leading-normal` | none | Body |
| Interface and small text | `--text-sm` | 400 to 500 | 1.5 | none | Body |
| Label, metadata | `--text-xs` | 500 | 1.5 | none | Body |
| Code | `--text-sm` | 400 | 1.6 | none | Mono |

Long reading pages may raise body text to 18px. Running text is never under 14px, and `--text-xs` is only for short labels.

## Hierarchy

- Use few sizes. A screen normally shows three or four.
- Make the jump between levels obvious. If two sizes look almost the same, use one.
- Big type needs tight line height and slight negative tracking. Small type needs neither.
- Portfolios and quiet personal sites may use a small h1, from `--text-h3` up, when the composition is built around it.
- App screens never use `--text-h1` or `--text-display`. Their titles are `--text-h3`.

## Line length

Aim for 60 to 75 characters. Under 45 feels choppy and over 90 is hard to follow. `--prose` sets this.

## Fonts

- Two families at most: display and body. One family with different weights is often better.
- Load with Fontsource, self-hosted, and only the weights you use.
- Prefer variable fonts.
- Use `font-display: swap` and preload the font used in the hero.
- Define a fallback with similar proportions, so text does not jump when the font loads.

## Details

- `text-wrap: balance` on headings, `text-wrap: pretty` on paragraphs.
- `font-variant-numeric: tabular-nums` for numbers in columns or that update.
- No text in images, unless it is a logo.
- The written-text rules, such as quotes and dashes, come from `COPY.md`.

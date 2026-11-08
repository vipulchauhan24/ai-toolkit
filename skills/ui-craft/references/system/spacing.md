# Spacing

Everything sits on a 4px grid. Use the `--space-*` tokens only.

## Page

| Thing | Value |
|---|---|
| Side margin | `--gutter`: 24px on phones, growing to 64px. Never under 16px at any width |
| Content width, most sections | `--container` |
| Reading width: articles and long text | `--prose` |
| Focused sections: FAQ, contact, a single statement | `--container-narrow` |
| Full-bleed images and colour bands | Up to `--container-wide`, or the full window. Their content stays in the container |
| Section padding, top and bottom | `--section` |
| Space above the first section under a fixed nav | `--nav-height` plus `--section` |

## Relationships

Space shows what belongs together. Inner space is always less than outer space.

| Between | Use |
|---|---|
| Letters of a label and its value | `--space-1` |
| Icon and its label | `--space-2` |
| Heading and the text under it | `--space-3` to `--space-4` |
| Paragraphs | `--space-4` |
| Form fields | `--space-5` |
| Items in a list of cards | `--grid-gap` |
| Section heading and section content | `--space-10` to `--space-12` |
| Two sections | `--section` from each |

Space above a heading is at least double the space below it.

## Inside components

| Component | Padding |
|---|---|
| Small card, list item | `--space-4` |
| Standard card | `--space-6` |
| Large feature card | `--space-8` to `--space-10` |
| Button | See `../components/button.md` |
| Modal | `--space-6`, `--space-8` from 768px |
| Table cell | `--space-3` vertical, `--space-4` horizontal |

## Density

`comfortable` is the default for websites. `compact` is for app screens with a lot of data: use one step smaller on padding and gaps, and `--control-sm` for toolbar controls. Touch targets stay at `--touch`.

## Grid

12 columns, `--grid-gap` between them, inside the container. On phones, one column.

Common spans at 1024px and above:

| Layout | Spans |
|---|---|
| Two equal | 6 + 6 |
| Text and media | 5 + 7, or 4 + 8 |
| Three across | 4 + 4 + 4 |
| Four across | 3 + 3 + 3 + 3 |

Choose the column count from how many items there are. Four items are never put in a three-column grid.

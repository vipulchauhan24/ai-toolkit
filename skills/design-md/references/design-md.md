# DESIGN.md

The project's design decisions, at the project root and committed. `scripts/deal.py` writes it from the chosen `concept.json`, along with `design.json` and `design.css`. Anyone working on the project later reads it and does not decide the look again.

## Format

It follows the DESIGN.md format from Google Stitch, version `alpha`: YAML front matter holding the design tokens, then markdown prose. The tokens are the values. The prose says how to use them.

Rules that make the file valid:

- The front matter starts and ends with a line that is exactly `---`.
- Token groups are `colors`, `typography`, `rounded`, `spacing` and `components`, plus `name`, `description` and `version`. A top-level key appears once in the whole file.
- Colours are any CSS colour. `primary` must exist. Dimensions use `px`, `em` or `rem` only.
- A reference is written `{colors.accent}` and points at a single value.
- Headings are `##`. Present sections keep this order: Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts. A heading appears once.
- Sections this skill adds go after Do's and Don'ts: Sections, Motion, Responsive. The format keeps unknown sections.
- Dark values are `colors` entries ending in `-dark`.

If npm is available, run `npx @google/design.md lint DESIGN.md` and fix every error. Without npm, check the rules above by hand and say the lint was not run. Never install anything to run it.

## After dealing

1. Write the sentences under "Overview", from the voice and fact sheet in `COPY.md`.
2. Remove any section the facts cannot support, from the "Sections" table and from `design.json`.
3. If the deal clashes with something the client already has, such as a logo colour, edit `DESIGN.md` and `design.css` together and run `contrast.py design.css`.

The "Colors" section is the role map: every token, its light and dark value, and what it is for. The page is built only from it.

Options set on `html`, from "Layout":

| Attribute | Values |
|---|---|
| `data-type` | `even` uses the scale as it is. `quiet` uses smaller headings and lets space do the work. `loud` makes headings a step larger |
| `data-bands` | `plain` has one background. `banded` alternates sections onto the surface colour. `ruled` puts a line between sections |
| `data-heads` | `left` puts section headings above their content. `side` puts them in a left column from 1024px. `center` centres them |
| `data-images` | `natural`, `framed` adds a thin mat, `mono` is greyscale until hovered, `none` means there are no images |

A change to a section or variant updates both `DESIGN.md` and `design.json`, because `sameness.py` reads `design.json`.

Do not re-deal to get a look you prefer. Use `--force` only when the user asks for a new direction.

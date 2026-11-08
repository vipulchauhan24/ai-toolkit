# DESIGN.md

The project's design decisions, at the project root and committed. `scripts/deal.py` writes it from the chosen `concept.json`, along with `design.json` and `design.css`. Anyone working on the project later reads it and does not decide the look again.

Its sections are: theme and atmosphere, colour, typography, shape, layout, sections, motion, do and don't, responsive.

After dealing:

1. Write the sentences under "Theme and atmosphere", from the voice and fact sheet in `COPY.md`.
2. Remove any section the facts cannot support.
3. If the deal clashes with something the client already has, such as a logo colour, edit `DESIGN.md` and `design.css` together and run `contrast.py design.css`.

Options set on `html`, from "Layout":

| Attribute | Values |
|---|---|
| `data-type` | `even` uses the scale as it is. `quiet` uses smaller headings and lets space do the work. `loud` makes headings a step larger |
| `data-bands` | `plain` has one background. `banded` alternates sections onto the surface colour. `ruled` puts a line between sections |
| `data-heads` | `left` puts section headings above their content. `side` puts them in a left column from 1024px. `center` centres them |
| `data-images` | `natural`, `framed` adds a thin mat, `mono` is greyscale until hovered, `none` means there are no images |

A build that changes a section or variant updates both `DESIGN.md` and `design.json`, because `sameness.py` reads `design.json`.

Do not re-deal to get a look you prefer. Use `--force` only when the user asks for a new direction.

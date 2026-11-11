# Colour

## Structure

Each palette defines the colour tokens in `system.md`, once for light and once for dark. Write values in OKLCH, with a hex fallback where the project needs one.

Build neutrals with a slight tint of the accent's hue, so that the greys belong to the palette.

## Colour combos

A project's colours come from one combo of 2 to 5 colours, each given a role. `assets/data/combos.json` holds the researched list, each tagged with the site kinds and audiences it suits. `scripts/colors.py build` turns every combo into a full palette in `assets/data/palettes.json`, in light and dark, and fails if any pair misses its minimum.

| Colours | Roles |
|---|---|
| 2 | `text` and `background`. The text colour also fills buttons |
| 3 | Plus `action`: the primary button, focus, and links when it reads as text |
| 4 | Plus `band`: banded section backgrounds and the footer |
| 5 | Plus `highlight` for tags, badges and markers, or `action-2` for a second button |

From the roles, the script derives the rest: lighter and darker shades of the text colour for body text, captions and lines, surfaces from the background, labels for each filled colour, and a dark theme built from the same hues. It never adds a hue. `DESIGN.md` lists every token with its use, before any code is written.

Rules the derivation follows:

- A label is light on a mid or dark fill and dark on a light one. Yellows, ambers and limes carry dark labels.
- Text links use the action colour only when it reaches 4.5:1 as text. Otherwise they are ink, underlined in the action colour.
- A filled colour must reach 3:1 against the page, so a pale yellow is a highlight, not a button.
- A band chooses its own text colour, so a dark band gets light text.

### The user's own colours

Write them to a file, then run `colors.py near` to show the closest combos beside them, unless the user wants their colours only. Strict use keeps their exact values; shades of them are still derived for secondary text, borders, surfaces and the dark theme.

```json
{
  "name": "Brand colours",
  "colors": { "ink": "#111111", "cream": "#F3EEE3", "orange": "#D9541E" },
  "roles": { "text": "ink", "background": "cream", "action": "orange" },
  "decisions": {}
}
```

A pair that fails is never changed silently. `colors.py derive` and `deal.py` print it as a CHOICE or a FAIL with options:

| Decision | Effect |
|---|---|
| `shade` | The nearest lightness of the same colour that passes |
| `large` | Keep the colour and the preferred label, set button labels at `--text-h3` bold, which needs only 3:1 |
| `other` | The other label colour, if it passes |
| `keep` | Accept the failing pair. `DESIGN.md` and `design.css` record that the owner chose it |

Put the options to the user, showing each one with the `near` command of `colors.py` and its HTML page, and record the answer under `decisions` (`on-accent`, `on-accent-2` or `text`).

### A second button colour

Use `--accent-2` only when the page has two distinct actions of similar weight, such as "Hire me" and "Read the case study", or "Start a trial" and "Book a demo". The concept sets `two_actions`. At most two filled button colours on a page, never for links or focus, and not on app screens, where a second filled colour means status. Otherwise the second button is an outline.

## Using colour

- One action colour. It marks the main action and a few points of emphasis. If everything is accented, nothing is. A second button colour follows the rule above.
- Neutrals do most of the work.
- Status colours mean status only: never use green or red as decoration.
- Never use colour alone to carry meaning. Add a word or icon.
- On app screens, keep colour for data, status and the main action.

## Contrast minimums

| Thing | Minimum |
|---|---|
| Normal text | 4.5:1 |
| Large text: 24px and up, or 18.5px bold and up | 3:1 |
| Control boundaries and meaningful icons | 3:1 |
| Focus ring against its surroundings | 3:1 |
| Placeholder text | 4.5:1 |

Disabled controls are exempt, but should still be readable. Text over photographs needs a scrim or a solid panel, measured against the brightest area behind it.

Check every text and background pair with the contrast script. Check both themes.

## Building a palette

1. Choose the accent's hue and how vivid it is.
2. Build a neutral ramp by changing lightness in even steps and keeping chroma very low.
3. Lower chroma as the lightness approaches white or black, so colours stay in range.
4. Assign roles: `--bg`, `--surface`, `--surface-2`, then the three inks, then lines.
5. Pick status colours that sit comfortably with the accent. If the accent is green, use it as `--positive`.
6. Test every pair.

## Dark theme

A dark theme is designed. Do not invert the light one.

- Backgrounds are very dark neutrals, tinted slightly. Use pure black only if the design is built around it.
- Raise a surface by making it lighter, since shadows barely show on dark.
- Reduce accent chroma slightly, so it does not vibrate against the background.
- Soft status backgrounds become dark tints.
- Body text is off-white, to lower glare.
- Set `color-scheme: dark`, and match `theme-color` to the page background.

## Avoid

- Purple-to-blue gradients on white or on black, the common default of generated pages.
- Gradient text as a habit.
- Glowing borders and neon on dark.
- Two action colours with no second action to justify them.
- A heavy coloured sidebar beside a light canvas.
